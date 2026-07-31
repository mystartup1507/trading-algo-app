import threading
import time

import MetaTrader5 as mt5

from connector import connector


class TradeLifecycleManager:

    JD_ALGO_MAGIC = 10001

    STATE_IDLE = "IDLE"
    STATE_PENDING = "PENDING"
    STATE_EXECUTING = "EXECUTING"
    STATE_OPEN = "OPEN"
    STATE_CLOSED = "CLOSED"
    STATE_FAILED = "FAILED"

    def __init__(self):

        self._lock = threading.Lock()

        self._states = {}

    # --------------------------------------------------
    # Normalize symbol
    # --------------------------------------------------

    def _normalize_symbol(self, symbol):

        if symbol is None:
            return ""

        return str(symbol).strip()

    # --------------------------------------------------
    # Get JD-Algo open positions
    # --------------------------------------------------

    def get_jd_positions(self, symbol=None):

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            symbol = self._normalize_symbol(symbol)

            if symbol:

                positions = mt5.positions_get(
                    symbol=symbol
                )

            else:

                positions = mt5.positions_get()

            if positions is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to retrieve MT5 positions."
                    ),
                    "mt5_error": mt5.last_error()
                }

            jd_positions = []

            for position in positions:

                if int(position.magic) != self.JD_ALGO_MAGIC:
                    continue

                jd_positions.append({
                    "ticket": int(position.ticket),
                    "symbol": position.symbol,
                    "volume": float(position.volume),
                    "price_open": float(
                        position.price_open
                    ),
                    "price_current": float(
                        position.price_current
                    ),
                    "sl": float(position.sl),
                    "tp": float(position.tp),
                    "profit": float(position.profit),
                    "magic": int(position.magic),
                    "comment": position.comment,
                    "direction": (
                        "BUY"
                        if position.type
                        == mt5.POSITION_TYPE_BUY
                        else "SELL"
                    )
                })

            return {
                "success": True,
                "message": (
                    f"{len(jd_positions)} "
                    "JD-Algo position(s) found."
                ),
                "data": {
                    "count": len(jd_positions),
                    "positions": jd_positions
                }
            }

        finally:

            connector.disconnect()

    # --------------------------------------------------
    # Duplicate-position protection
    # --------------------------------------------------

    def check_duplicate(self, symbol):

        symbol = self._normalize_symbol(symbol)

        if not symbol:

            return {
                "success": False,
                "message": "Symbol is required."
            }

        result = self.get_jd_positions(
            symbol=symbol
        )

        if not result["success"]:
            return result

        positions = result["data"]["positions"]

        duplicate = len(positions) > 0

        return {
            "success": True,
            "message": (
                "Existing JD-Algo position detected."
                if duplicate
                else "No duplicate JD-Algo position detected."
            ),
            "data": {
                "symbol": symbol,
                "duplicate": duplicate,
                "count": len(positions),
                "positions": positions
            }
        }

    # --------------------------------------------------
    # Execution lock
    #
    # Prevent two requests from entering the execution
    # section simultaneously.
    # --------------------------------------------------

    def acquire_execution_lock(self):

        acquired = self._lock.acquire(
            blocking=False
        )

        return {
            "success": acquired,
            "message": (
                "Execution lock acquired."
                if acquired
                else "Another trade execution is already in progress."
            ),
            "data": {
                "locked": acquired
            }
        }

    def release_execution_lock(self):

        if self._lock.locked():

            self._lock.release()

        return {
            "success": True,
            "message": "Execution lock released."
        }

    # --------------------------------------------------
    # Trade state
    # --------------------------------------------------

    def set_state(
        self,
        symbol,
        state,
        metadata=None
    ):

        symbol = self._normalize_symbol(symbol)

        if not symbol:

            return {
                "success": False,
                "message": "Symbol is required."
            }

        allowed_states = {
            self.STATE_IDLE,
            self.STATE_PENDING,
            self.STATE_EXECUTING,
            self.STATE_OPEN,
            self.STATE_CLOSED,
            self.STATE_FAILED
        }

        if state not in allowed_states:

            return {
                "success": False,
                "message": (
                    f"Invalid trade state '{state}'."
                )
            }

        self._states[symbol] = {
            "symbol": symbol,
            "state": state,
            "updated_at": time.time(),
            "metadata": metadata or {}
        }

        return {
            "success": True,
            "message": "Trade state updated.",
            "data": self._states[symbol]
        }

    def get_state(self, symbol):

        symbol = self._normalize_symbol(symbol)

        if not symbol:

            return {
                "success": False,
                "message": "Symbol is required."
            }

        state = self._states.get(symbol)

        if state is None:

            state = {
                "symbol": symbol,
                "state": self.STATE_IDLE,
                "updated_at": None,
                "metadata": {}
            }

        return {
            "success": True,
            "message": "Trade state retrieved.",
            "data": state
        }

    # --------------------------------------------------
    # Recover state directly from MT5
    #
    # MT5 is the source of truth after backend restart.
    # --------------------------------------------------

    def recover_state(self, symbol):

        symbol = self._normalize_symbol(symbol)

        duplicate_result = self.check_duplicate(
            symbol
        )

        if not duplicate_result["success"]:
            return duplicate_result

        positions = (
            duplicate_result["data"]["positions"]
        )

        if positions:

            state = self.STATE_OPEN

            metadata = {
                "recovered": True,
                "positions": positions
            }

        else:

            state = self.STATE_IDLE

            metadata = {
                "recovered": True,
                "positions": []
            }

        result = self.set_state(
            symbol=symbol,
            state=state,
            metadata=metadata
        )

        if not result["success"]:
            return result

        return {
            "success": True,
            "message": (
                "Trade lifecycle state recovered "
                "from MT5."
            ),
            "data": result["data"]
        }

    # --------------------------------------------------
    # Pre-execution reliability check
    # --------------------------------------------------

    def pre_execution_check(self, symbol):

        symbol = self._normalize_symbol(symbol)

        if not symbol:

            return {
                "success": False,
                "message": "Symbol is required."
            }

        duplicate_result = self.check_duplicate(
            symbol
        )

        if not duplicate_result["success"]:
            return duplicate_result

        duplicate = (
            duplicate_result["data"]["duplicate"]
        )

        state_result = self.get_state(symbol)

        if not state_result["success"]:
            return state_result

        state = state_result["data"]["state"]

        blocked_states = {
            self.STATE_PENDING,
            self.STATE_EXECUTING,
            self.STATE_OPEN
        }

        checks = {
            "duplicate_position": not duplicate,
            "lifecycle_state": (
                state not in blocked_states
            )
        }

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        allowed = len(failed_checks) == 0

        return {
            "success": allowed,
            "message": (
                "Pre-execution reliability checks passed."
                if allowed
                else "Trade blocked by execution reliability layer."
            ),
            "data": {
                "allowed": allowed,
                "symbol": symbol,
                "state": state,
                "checks": checks,
                "failed_checks": failed_checks,
                "duplicate": (
                    duplicate_result["data"]
                )
            }
        }


trade_lifecycle_manager = TradeLifecycleManager()