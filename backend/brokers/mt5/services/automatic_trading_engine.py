import copy
import threading
import time
from datetime import datetime, timezone

from services.automated_trade_pipeline import (
    automated_trade_pipeline
)


class AutomaticTradingEngine:

    DEFAULT_SYMBOL = "EURUSD#"
    DEFAULT_TIMEFRAME = "M15"

    DEFAULT_RISK_PERCENT = 1.0
    DEFAULT_ATR_MULTIPLIER = 2.0
    DEFAULT_RISK_REWARD = 2.0

    DEFAULT_SCAN_INTERVAL = 60.0

    MIN_SCAN_INTERVAL = 5.0
    MAX_SCAN_INTERVAL = 3600.0

    def __init__(self):

        self._state_lock = threading.RLock()

        self._worker_thread = None
        self._stop_event = threading.Event()

        self._running = False

        self._started_at = None
        self._stopped_at = None
        self._last_scan_at = None
        self._next_scan_at = None

        self._scan_count = 0
        self._error_count = 0

        self._last_result = None
        self._last_error = None

        self._config = self._default_config()

    # ==================================================
    # INTERNAL HELPERS
    # ==================================================

    def _default_config(self):

        return {
            "symbol": self.DEFAULT_SYMBOL,
            "timeframe": self.DEFAULT_TIMEFRAME,
            "risk_percent": (
                self.DEFAULT_RISK_PERCENT
            ),
            "atr_multiplier": (
                self.DEFAULT_ATR_MULTIPLIER
            ),
            "risk_reward": (
                self.DEFAULT_RISK_REWARD
            ),
            "scan_interval": (
                self.DEFAULT_SCAN_INTERVAL
            ),

            # ------------------------------------------
            # Phase 10.5 safety barrier
            #
            # The continuous engine is intentionally
            # dry-run only at this stage.
            # ------------------------------------------

            "dry_run": True
        }

    def _utc_now(self):

        return datetime.now(
            timezone.utc
        ).isoformat()

    def _timestamp_after(self, seconds):

        return datetime.fromtimestamp(
            time.time() + float(seconds),
            tz=timezone.utc
        ).isoformat()

    def _thread_alive(self):

        return (
            self._worker_thread is not None
            and self._worker_thread.is_alive()
        )

    # ==================================================
    # CONFIGURATION VALIDATION
    # ==================================================

    def _validate_config(
        self,
        symbol,
        timeframe,
        risk_percent,
        atr_multiplier,
        risk_reward,
        scan_interval
    ):

        symbol = str(
            symbol or ""
        ).strip()

        timeframe = str(
            timeframe or ""
        ).strip().upper()

        if not symbol:

            return {
                "success": False,
                "message": (
                    "Symbol is required."
                )
            }

        if not timeframe:

            return {
                "success": False,
                "message": (
                    "Timeframe is required."
                )
            }

        try:

            risk_percent = float(
                risk_percent
            )

            atr_multiplier = float(
                atr_multiplier
            )

            risk_reward = float(
                risk_reward
            )

            scan_interval = float(
                scan_interval
            )

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": (
                    "Risk percent, ATR multiplier, "
                    "risk/reward and scan interval "
                    "must be valid numbers."
                )
            }

        if risk_percent <= 0:

            return {
                "success": False,
                "message": (
                    "Risk percent must be greater "
                    "than zero."
                )
            }

        # ----------------------------------------------
        # Do not allow the continuous engine to request
        # risk beyond the Phase 10.3 policy.
        # The Exposure Guard remains the independent
        # second line of defence.
        # ----------------------------------------------

        if risk_percent > 1.0:

            return {
                "success": False,
                "message": (
                    "Automatic trading engine risk "
                    "cannot exceed 1.0 percent."
                )
            }

        if atr_multiplier <= 0:

            return {
                "success": False,
                "message": (
                    "ATR multiplier must be greater "
                    "than zero."
                )
            }

        if risk_reward <= 0:

            return {
                "success": False,
                "message": (
                    "Risk/reward must be greater "
                    "than zero."
                )
            }

        if (
            scan_interval
            < self.MIN_SCAN_INTERVAL
        ):

            return {
                "success": False,
                "message": (
                    "Scan interval cannot be less "
                    f"than {self.MIN_SCAN_INTERVAL} "
                    "seconds."
                )
            }

        if (
            scan_interval
            > self.MAX_SCAN_INTERVAL
        ):

            return {
                "success": False,
                "message": (
                    "Scan interval cannot exceed "
                    f"{self.MAX_SCAN_INTERVAL} "
                    "seconds."
                )
            }

        return {
            "success": True,
            "message": (
                "Automatic trading configuration "
                "validated."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "risk_percent": risk_percent,
                "atr_multiplier": (
                    atr_multiplier
                ),
                "risk_reward": (
                    risk_reward
                ),
                "scan_interval": (
                    scan_interval
                ),

                # --------------------------------------
                # Hard-coded safety mode.
                # --------------------------------------

                "dry_run": True
            }
        }

    # ==================================================
    # START
    # ==================================================

    def start(
        self,
        symbol=None,
        timeframe=None,
        risk_percent=None,
        atr_multiplier=None,
        risk_reward=None,
        scan_interval=None
    ):

        with self._state_lock:

            if (
                self._running
                or self._thread_alive()
            ):

                return {
                    "success": False,
                    "message": (
                        "Automatic trading engine "
                        "is already running."
                    ),
                    "data": self._status_data()
                }

            defaults = (
                self._default_config()
            )

            validation = (
                self._validate_config(
                    symbol=(
                        symbol
                        if symbol is not None
                        else defaults["symbol"]
                    ),
                    timeframe=(
                        timeframe
                        if timeframe is not None
                        else defaults["timeframe"]
                    ),
                    risk_percent=(
                        risk_percent
                        if risk_percent is not None
                        else defaults[
                            "risk_percent"
                        ]
                    ),
                    atr_multiplier=(
                        atr_multiplier
                        if atr_multiplier is not None
                        else defaults[
                            "atr_multiplier"
                        ]
                    ),
                    risk_reward=(
                        risk_reward
                        if risk_reward is not None
                        else defaults[
                            "risk_reward"
                        ]
                    ),
                    scan_interval=(
                        scan_interval
                        if scan_interval is not None
                        else defaults[
                            "scan_interval"
                        ]
                    )
                )
            )

            if not validation["success"]:
                return validation

            self._config = copy.deepcopy(
                validation["data"]
            )

            self._stop_event.clear()

            self._running = True

            self._started_at = (
                self._utc_now()
            )

            self._stopped_at = None
            self._last_scan_at = None
            self._next_scan_at = (
                self._utc_now()
            )

            self._scan_count = 0
            self._error_count = 0

            self._last_result = None
            self._last_error = None

            self._worker_thread = (
                threading.Thread(
                    target=self._worker_loop,
                    name=(
                        "JD-Algo-"
                        "AutomaticTradingEngine"
                    ),
                    daemon=True
                )
            )

            self._worker_thread.start()

            return {
                "success": True,
                "message": (
                    "Automatic trading engine "
                    "started in DRY-RUN mode."
                ),
                "data": self._status_data()
            }

    # ==================================================
    # STOP
    # ==================================================

    def stop(self):

        with self._state_lock:

            if (
                not self._running
                and not self._thread_alive()
            ):

                return {
                    "success": False,
                    "message": (
                        "Automatic trading engine "
                        "is not running."
                    ),
                    "data": self._status_data()
                }

            self._stop_event.set()

            worker = self._worker_thread

        # ----------------------------------------------
        # Do not hold the state lock while joining.
        # The worker may need that same lock while
        # shutting down.
        # ----------------------------------------------

        if (
            worker is not None
            and worker is not threading.current_thread()
        ):

            worker.join(
                timeout=5.0
            )

        with self._state_lock:

            if self._thread_alive():

                return {
                    "success": False,
                    "message": (
                        "Stop signal was sent but "
                        "the worker is still shutting "
                        "down."
                    ),
                    "data": self._status_data()
                }

            self._running = False
            self._next_scan_at = None

            if self._stopped_at is None:
                self._stopped_at = (
                    self._utc_now()
                )

            return {
                "success": True,
                "message": (
                    "Automatic trading engine "
                    "stopped successfully."
                ),
                "data": self._status_data()
            }

    # ==================================================
    # STATUS
    # ==================================================

    def status(self):

        with self._state_lock:

            return {
                "success": True,
                "message": (
                    "Automatic trading engine "
                    "status retrieved."
                ),
                "data": self._status_data()
            }

    def _status_data(self):

        return {
            "running": bool(
                self._running
            ),
            "worker_alive": bool(
                self._thread_alive()
            ),
            "mode": "DRY_RUN",
            "config": copy.deepcopy(
                self._config
            ),
            "started_at": (
                self._started_at
            ),
            "stopped_at": (
                self._stopped_at
            ),
            "last_scan_at": (
                self._last_scan_at
            ),
            "next_scan_at": (
                self._next_scan_at
            ),
            "scan_count": int(
                self._scan_count
            ),
            "error_count": int(
                self._error_count
            ),
            "last_result": copy.deepcopy(
                self._last_result
            ),
            "last_error": copy.deepcopy(
                self._last_error
            )
        }

    # ==================================================
    # WORKER LOOP
    # ==================================================

    def _worker_loop(self):

        try:

            while not self._stop_event.is_set():

                with self._state_lock:

                    config = copy.deepcopy(
                        self._config
                    )

                    self._last_scan_at = (
                        self._utc_now()
                    )

                    self._next_scan_at = None

                try:

                    # ----------------------------------
                    # Continuous engine remains
                    # DRY-RUN ONLY in Phase 10.5.
                    # ----------------------------------

                    result = (
                        automated_trade_pipeline.run(
                            symbol=(
                                config["symbol"]
                            ),
                            timeframe=(
                                config[
                                    "timeframe"
                                ]
                            ),
                            risk_percent=(
                                config[
                                    "risk_percent"
                                ]
                            ),
                            atr_multiplier=(
                                config[
                                    "atr_multiplier"
                                ]
                            ),
                            risk_reward=(
                                config[
                                    "risk_reward"
                                ]
                            ),
                            dry_run=True
                        )
                    )

                    with self._state_lock:

                        self._scan_count += 1

                        self._last_result = (
                            copy.deepcopy(
                                result
                            )
                        )

                        self._last_error = None

                except Exception as error:

                    with self._state_lock:

                        self._scan_count += 1
                        self._error_count += 1

                        self._last_error = {
                            "message": str(
                                error
                            ),
                            "time": (
                                self._utc_now()
                            )
                        }

                if self._stop_event.is_set():
                    break

                interval = float(
                    config["scan_interval"]
                )

                with self._state_lock:

                    self._next_scan_at = (
                        self._timestamp_after(
                            interval
                        )
                    )

                # --------------------------------------
                # Event.wait() is used instead of
                # time.sleep() so STOP can interrupt
                # the waiting period immediately.
                # --------------------------------------

                if self._stop_event.wait(
                    interval
                ):
                    break

        finally:

            with self._state_lock:

                self._running = False
                self._next_scan_at = None
                self._stopped_at = (
                    self._utc_now()
                )


automatic_trading_engine = (
    AutomaticTradingEngine()
)