import threading
import time
import uuid
from datetime import datetime, timezone

from services.automated_trade_pipeline import automated_trade_pipeline
from trade_execution.trade_lifecycle_manager import trade_lifecycle_manager


class AutomaticTradingEngine:

    # ======================================================
    # Safety / reliability configuration
    # ======================================================

    DEFAULT_SCAN_INTERVAL = 5.0
    MIN_SCAN_INTERVAL = 1.0

    # Stop the continuous worker after this many consecutive
    # unexpected engine/infrastructure exceptions.
    MAX_CONSECUTIVE_ERRORS = 5

    def __init__(self):

        # --------------------------------------------------
        # Engine state protection
        # --------------------------------------------------

        self._state_lock = threading.RLock()

        # Prevent overlapping scan cycles inside this engine.
        #
        # IMPORTANT:
        # This is intentionally separate from the lifecycle
        # manager's execution lock. The lifecycle execution
        # lock protects actual order execution. This lock
        # protects continuous scan-cycle integrity.
        self._scan_lock = threading.Lock()

        # --------------------------------------------------
        # Worker
        # --------------------------------------------------

        self._thread = None
        self._stop_event = threading.Event()

        # Every start receives a unique run ID. This prevents
        # an old worker from continuing after a later restart.
        self._run_id = None

        self._running = False

        # --------------------------------------------------
        # Configuration
        # --------------------------------------------------

        self._config = {}

        # --------------------------------------------------
        # Runtime statistics
        # --------------------------------------------------

        self._scan_count = 0
        self._successful_scan_count = 0
        self._failed_scan_count = 0
        self._error_count = 0
        self._consecutive_errors = 0
        self._overlap_skip_count = 0

        # --------------------------------------------------
        # Runtime results
        # --------------------------------------------------

        self._last_result = None
        self._last_successful_result = None
        self._last_error = None

        self._last_scan_at = None
        self._last_scan_completed_at = None
        self._last_scan_duration = None
        self._next_scan_at = None

        # --------------------------------------------------
        # Lifecycle recovery information
        # --------------------------------------------------

        self._last_lifecycle_recovery = None

        # --------------------------------------------------
        # Start / stop information
        # --------------------------------------------------

        self._started_at = None
        self._stopped_at = None
        self._stop_reason = None

    # ======================================================
    # Time helpers
    # ======================================================

    def _utc_now(self):

        return datetime.now(
            timezone.utc
        )

    def _utc_iso(self):

        return self._utc_now().isoformat()

    # ======================================================
    # Value normalization
    # ======================================================

    def _normalize_symbol(self, symbol):

        if symbol is None:
            return ""

        return str(symbol).strip()

    def _normalize_timeframe(self, timeframe):

        if timeframe is None:
            return ""

        return str(timeframe).strip().upper()

    # ======================================================
    # Configuration validation
    # ======================================================

    def _build_config(
        self,
        symbol,
        timeframe,
        risk_percent,
        atr_multiplier,
        risk_reward,
        scan_interval
    ):

        symbol = self._normalize_symbol(symbol)
        timeframe = self._normalize_timeframe(timeframe)

        if not symbol:

            return {
                "success": False,
                "message": "symbol is required."
            }

        if not timeframe:

            return {
                "success": False,
                "message": "timeframe is required."
            }

        try:

            risk_percent = float(
                1.0
                if risk_percent is None
                else risk_percent
            )

            atr_multiplier = float(
                2.0
                if atr_multiplier is None
                else atr_multiplier
            )

            risk_reward = float(
                2.0
                if risk_reward is None
                else risk_reward
            )

            scan_interval = float(
                self.DEFAULT_SCAN_INTERVAL
                if scan_interval is None
                else scan_interval
            )

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": (
                    "risk_percent, atr_multiplier, "
                    "risk_reward and scan_interval "
                    "must be valid numbers."
                )
            }

        if risk_percent <= 0:

            return {
                "success": False,
                "message": (
                    "risk_percent must be greater than 0."
                )
            }

        if atr_multiplier <= 0:

            return {
                "success": False,
                "message": (
                    "atr_multiplier must be greater than 0."
                )
            }

        if risk_reward <= 0:

            return {
                "success": False,
                "message": (
                    "risk_reward must be greater than 0."
                )
            }

        if scan_interval < self.MIN_SCAN_INTERVAL:

            return {
                "success": False,
                "message": (
                    "scan_interval must be at least "
                    f"{self.MIN_SCAN_INTERVAL} second(s)."
                )
            }

        # --------------------------------------------------
        # CRITICAL SAFETY BARRIER
        #
        # Continuous automatic trading remains DRY-RUN ONLY.
        # There is intentionally no API parameter capable of
        # changing this value.
        # --------------------------------------------------

        config = {
            "symbol": symbol,
            "timeframe": timeframe,
            "risk_percent": risk_percent,
            "atr_multiplier": atr_multiplier,
            "risk_reward": risk_reward,
            "scan_interval": scan_interval,
            "dry_run": True
        }

        return {
            "success": True,
            "message": (
                "Automatic trading configuration validated."
            ),
            "data": config
        }

    # ======================================================
    # Worker identity
    # ======================================================

    def _is_current_run(self, run_id):

        with self._state_lock:

            return (
                self._run_id == run_id
                and self._running
            )

    # ======================================================
    # Lifecycle recovery
    # ======================================================

    def _recover_lifecycle(self, symbol):

        result = (
            trade_lifecycle_manager
            .recover_state(symbol)
        )

        with self._state_lock:

            self._last_lifecycle_recovery = result

        return result

    # ======================================================
    # Scan classification
    # ======================================================

    def _classify_result(self, result):

        if not isinstance(result, dict):

            return {
                "success": False,
                "stage": "INVALID_RESULT",
                "message": (
                    "Automated trade pipeline returned "
                    "an invalid result."
                )
            }

        data = result.get("data") or {}

        return {
            "success": bool(
                result.get("success", False)
            ),
            "stage": data.get("stage"),
            "message": result.get(
                "message",
                "Pipeline scan completed."
            )
        }

    # ======================================================
    # Execute one scan
    # ======================================================

    def _run_scan(self, run_id):

        # --------------------------------------------------
        # Do not allow overlapping scans.
        # --------------------------------------------------

        acquired = self._scan_lock.acquire(
            blocking=False
        )

        if not acquired:

            with self._state_lock:

                self._overlap_skip_count += 1

            return {
                "success": False,
                "message": (
                    "Scan skipped because another scan "
                    "cycle is still in progress."
                ),
                "data": {
                    "stage": "SCAN_OVERLAP",
                    "executed": False
                }
            }

        scan_started_monotonic = time.monotonic()
        scan_started_at = self._utc_iso()

        try:

            if not self._is_current_run(run_id):

                return {
                    "success": False,
                    "message": (
                        "Scan cancelled because this worker "
                        "is no longer the active engine run."
                    ),
                    "data": {
                        "stage": "STALE_WORKER",
                        "executed": False
                    }
                }

            with self._state_lock:

                config = dict(self._config)

                self._scan_count += 1
                self._last_scan_at = scan_started_at

            symbol = config["symbol"]

            # --------------------------------------------------
            # Recover lifecycle from MT5 before each scan.
            #
            # MT5 remains the source of truth.
            # --------------------------------------------------

            lifecycle_result = (
                self._recover_lifecycle(symbol)
            )

            if not lifecycle_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Automatic scan blocked because "
                        "MT5 lifecycle recovery failed."
                    ),
                    "data": {
                        "stage": "LIFECYCLE_RECOVERY",
                        "executed": False,
                        "recovery": lifecycle_result
                    }
                }

            if not self._is_current_run(run_id):

                return {
                    "success": False,
                    "message": (
                        "Scan cancelled because the engine "
                        "was stopped during lifecycle recovery."
                    ),
                    "data": {
                        "stage": "STOPPED",
                        "executed": False
                    }
                }

            # --------------------------------------------------
            # Automatic trade pipeline
            #
            # CRITICAL:
            # dry_run=True remains hard-coded here.
            # --------------------------------------------------

            result = automated_trade_pipeline.run(
                symbol=config["symbol"],
                timeframe=config["timeframe"],
                risk_percent=config["risk_percent"],
                atr_multiplier=config[
                    "atr_multiplier"
                ],
                risk_reward=config["risk_reward"],
                dry_run=True
            )

            return result

        finally:

            duration = (
                time.monotonic()
                - scan_started_monotonic
            )

            with self._state_lock:

                self._last_scan_duration = round(
                    duration,
                    4
                )

                self._last_scan_completed_at = (
                    self._utc_iso()
                )

            self._scan_lock.release()

    # ======================================================
    # Process scan result
    # ======================================================

    def _record_scan_result(self, result):

        classification = self._classify_result(
            result
        )

        with self._state_lock:

            self._last_result = result

            if classification["success"]:

                self._successful_scan_count += 1

                self._last_successful_result = (
                    result
                )

                # A normal pipeline response means the
                # infrastructure cycle completed correctly.
                #
                # HOLD / NO_TRADE is therefore not an engine
                # error.
                self._consecutive_errors = 0

                self._last_error = None

            else:

                self._failed_scan_count += 1

                # A pipeline rejection is recorded, but is
                # not automatically treated as an unexpected
                # engine exception.
                #
                # Exposure guard, trade validation, lifecycle
                # protection, etc. may intentionally reject a
                # trade.
                self._consecutive_errors = 0

    # ======================================================
    # Record unexpected engine exception
    # ======================================================

    def _record_exception(self, error):

        error_data = {
            "type": type(error).__name__,
            "message": str(error),
            "timestamp": self._utc_iso()
        }

        with self._state_lock:

            self._error_count += 1
            self._failed_scan_count += 1
            self._consecutive_errors += 1

            self._last_error = error_data

            self._last_result = {
                "success": False,
                "message": (
                    "Automatic trading engine scan error: "
                    f"{str(error)}"
                ),
                "data": {
                    "stage": "ENGINE_ERROR",
                    "executed": False,
                    "error": error_data
                }
            }

        return error_data

    # ======================================================
    # Automatic emergency stop
    # ======================================================

    def _should_emergency_stop(self):

        with self._state_lock:

            return (
                self._consecutive_errors
                >= self.MAX_CONSECUTIVE_ERRORS
            )

    def _emergency_stop(self, run_id):

        with self._state_lock:

            if self._run_id != run_id:
                return

            self._running = False
            self._stop_reason = (
                "Automatic engine stopped after "
                f"{self.MAX_CONSECUTIVE_ERRORS} "
                "consecutive engine errors."
            )

            self._stopped_at = self._utc_iso()
            self._next_scan_at = None

        self._stop_event.set()

    # ======================================================
    # Worker loop
    # ======================================================

    def _worker(self, run_id):

        try:

            while True:

                if self._stop_event.is_set():
                    break

                if not self._is_current_run(run_id):
                    break

                cycle_started = time.monotonic()

                try:

                    result = self._run_scan(
                        run_id
                    )

                    # Do not let an obsolete worker update
                    # the state of a later engine run.
                    if not self._is_current_run(
                        run_id
                    ):
                        break

                    self._record_scan_result(
                        result
                    )

                except Exception as error:

                    if not self._is_current_run(
                        run_id
                    ):
                        break

                    self._record_exception(
                        error
                    )

                    if self._should_emergency_stop():

                        self._emergency_stop(
                            run_id
                        )

                        break

                if not self._is_current_run(run_id):
                    break

                with self._state_lock:

                    scan_interval = float(
                        self._config.get(
                            "scan_interval",
                            self.DEFAULT_SCAN_INTERVAL
                        )
                    )

                elapsed = (
                    time.monotonic()
                    - cycle_started
                )

                wait_seconds = max(
                    0.0,
                    scan_interval - elapsed
                )

                with self._state_lock:

                    if (
                        self._run_id == run_id
                        and self._running
                    ):

                        self._next_scan_at = (
                            datetime.fromtimestamp(
                                time.time()
                                + wait_seconds,
                                tz=timezone.utc
                            ).isoformat()
                        )

                # Interruptible wait.
                #
                # /algo/stop can wake the worker
                # immediately instead of waiting for the
                # complete scan interval.
                if self._stop_event.wait(
                    wait_seconds
                ):
                    break

        finally:

            with self._state_lock:

                # Only the currently active run may change
                # global engine running state.
                if self._run_id == run_id:

                    self._running = False
                    self._next_scan_at = None

                    if self._stopped_at is None:
                        self._stopped_at = (
                            self._utc_iso()
                        )

                    if self._stop_reason is None:
                        self._stop_reason = (
                            "Automatic trading worker exited."
                        )

    # ======================================================
    # Start
    # ======================================================

    def start(
        self,
        symbol=None,
        timeframe=None,
        risk_percent=None,
        atr_multiplier=None,
        risk_reward=None,
        scan_interval=None
    ):

        config_result = self._build_config(
            symbol=symbol,
            timeframe=timeframe,
            risk_percent=risk_percent,
            atr_multiplier=atr_multiplier,
            risk_reward=risk_reward,
            scan_interval=scan_interval
        )

        if not config_result["success"]:
            return config_result

        config = config_result["data"]

        with self._state_lock:

            if (
                self._running
                and self._thread is not None
                and self._thread.is_alive()
            ):

                return {
                    "success": False,
                    "message": (
                        "Automatic trading engine "
                        "is already running."
                    ),
                    "data": self._status_data_locked()
                }

            # --------------------------------------------------
            # A previous thread should never be allowed to
            # survive into a new run.
            # --------------------------------------------------

            if (
                self._thread is not None
                and self._thread.is_alive()
            ):

                return {
                    "success": False,
                    "message": (
                        "Previous automatic trading worker "
                        "is still shutting down."
                    ),
                    "data": self._status_data_locked()
                }

            run_id = uuid.uuid4().hex

            self._run_id = run_id

            self._config = dict(config)

            self._stop_event = threading.Event()

            self._running = True

            # --------------------------------------------------
            # Reset per-run statistics
            # --------------------------------------------------

            self._scan_count = 0
            self._successful_scan_count = 0
            self._failed_scan_count = 0
            self._error_count = 0
            self._consecutive_errors = 0
            self._overlap_skip_count = 0

            self._last_result = None
            self._last_successful_result = None
            self._last_error = None

            self._last_scan_at = None
            self._last_scan_completed_at = None
            self._last_scan_duration = None

            self._last_lifecycle_recovery = None

            self._started_at = self._utc_iso()
            self._stopped_at = None
            self._stop_reason = None

            self._next_scan_at = (
                self._started_at
            )

            self._thread = threading.Thread(
                target=self._worker,
                args=(run_id,),
                name=(
                    "JD-Algo-AutomaticTradingEngine"
                ),
                daemon=True
            )

            self._thread.start()

            data = self._status_data_locked()

        return {
            "success": True,
            "message": (
                "Automatic trading engine started "
                "in DRY-RUN mode."
            ),
            "data": data
        }

    # ======================================================
    # Stop
    # ======================================================

    def stop(self):

        with self._state_lock:

            thread = self._thread

            if (
                not self._running
                and (
                    thread is None
                    or not thread.is_alive()
                )
            ):

                return {
                    "success": True,
                    "message": (
                        "Automatic trading engine "
                        "is already stopped."
                    ),
                    "data": self._status_data_locked()
                }

            self._running = False
            self._stop_reason = (
                "Automatic trading engine stopped "
                "by API request."
            )

            self._stopped_at = self._utc_iso()
            self._next_scan_at = None

            stop_event = self._stop_event

        # --------------------------------------------------
        # Signal outside state lock.
        # --------------------------------------------------

        stop_event.set()

        # --------------------------------------------------
        # Do not hold the state lock while joining.
        # The worker may need the same lock to exit.
        # --------------------------------------------------

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):

            thread.join(timeout=5.0)

        with self._state_lock:

            data = self._status_data_locked()

        return {
            "success": True,
            "message": (
                "Automatic trading engine stop "
                "request completed."
            ),
            "data": data
        }

    # ======================================================
    # Status internals
    # ======================================================

    def _status_data_locked(self):

        thread = self._thread

        worker_alive = bool(
            thread is not None
            and thread.is_alive()
        )

        scan_in_progress = (
            self._scan_lock.locked()
        )

        return {
            "running": bool(self._running),
            "mode": "DRY_RUN",
            "run_id": self._run_id,
            "config": dict(self._config),

            "worker_alive": worker_alive,
            "worker_name": (
                thread.name
                if thread is not None
                else None
            ),

            "scan_in_progress": (
                scan_in_progress
            ),

            "scan_count": self._scan_count,
            "successful_scan_count": (
                self._successful_scan_count
            ),
            "failed_scan_count": (
                self._failed_scan_count
            ),
            "error_count": self._error_count,
            "consecutive_errors": (
                self._consecutive_errors
            ),
            "maximum_consecutive_errors": (
                self.MAX_CONSECUTIVE_ERRORS
            ),
            "overlap_skip_count": (
                self._overlap_skip_count
            ),

            "last_scan_at": self._last_scan_at,
            "last_scan_completed_at": (
                self._last_scan_completed_at
            ),
            "last_scan_duration_seconds": (
                self._last_scan_duration
            ),
            "next_scan_at": self._next_scan_at,

            "last_result": self._last_result,
            "last_successful_result": (
                self._last_successful_result
            ),
            "last_error": self._last_error,

            "last_lifecycle_recovery": (
                self._last_lifecycle_recovery
            ),

            "started_at": self._started_at,
            "stopped_at": self._stopped_at,
            "stop_reason": self._stop_reason
        }

    # ======================================================
    # Public status
    # ======================================================

    def status(self):

        with self._state_lock:

            data = self._status_data_locked()

        return {
            "success": True,
            "message": (
                "Automatic trading engine status retrieved."
            ),
            "data": data
        }


automatic_trading_engine = AutomaticTradingEngine()