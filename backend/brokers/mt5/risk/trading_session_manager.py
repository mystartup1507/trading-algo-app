from datetime import datetime, time, timezone
import MetaTrader5 as mt5

from connector import connector


class TradingSessionManager:

    # =====================================================
    # SESSION CONFIGURATION
    # =====================================================

    ENABLE_ASIAN = False
    ENABLE_LONDON = True
    ENABLE_NEW_YORK = True

    # =====================================================
    # TRADING HOURS (UTC)
    # =====================================================

    TRADING_START = time(7, 0)
    TRADING_END = time(22, 0)

    # =====================================================
    # SESSION HOURS (UTC)
    # =====================================================

    ASIAN_START = time(0, 0)
    ASIAN_END = time(8, 0)

    LONDON_START = time(7, 0)
    LONDON_END = time(16, 0)

    NEW_YORK_START = time(12, 0)
    NEW_YORK_END = time(21, 0)

    # =====================================================

    def _utc_now(self):

        return datetime.now(timezone.utc)

    # =====================================================

    def is_weekend(self):

        now = self._utc_now()

        # Saturday
        if now.weekday() == 5:
            return True

        # Sunday before market open
        if now.weekday() == 6 and now.hour < 21:
            return True

        # Friday after market close
        if now.weekday() == 4 and now.hour >= 21:
            return True

        return False

    # =====================================================

    def is_market_open(self, symbol):

        status = connector.connect()

        if not status["success"]:

            return {
                "success": False,
                "message": "Unable to connect to MT5."
            }

        try:

            info = mt5.symbol_info(symbol)

            if info is None:

                return {
                    "success": False,
                    "message": "Symbol not found."
                }

            trade_enabled = (
                info.trade_mode != mt5.SYMBOL_TRADE_MODE_DISABLED
            )

            return {
                "success": True,
                "data": {
                    "market_open": trade_enabled,
                    "trade_mode": info.trade_mode
                }
            }

        finally:

            connector.disconnect()

    # =====================================================

    def is_trading_time(self):

        now = self._utc_now().time()

        return (
            self.TRADING_START
            <= now
            <= self.TRADING_END
        )

    # =====================================================

    def is_session_allowed(self):

        now = self._utc_now().time()

        if (
            self.ASIAN_START
            <= now
            <= self.ASIAN_END
        ):

            return self.ENABLE_ASIAN

        if (
            self.LONDON_START
            <= now
            <= self.LONDON_END
        ):

            return self.ENABLE_LONDON

        if (
            self.NEW_YORK_START
            <= now
            <= self.NEW_YORK_END
        ):

            return self.ENABLE_NEW_YORK

        return False

    # =====================================================

    def validate(self, symbol):

        checks = {}

        checks["weekend"] = not self.is_weekend()

        checks["trading_hours"] = self.is_trading_time()

        checks["session"] = self.is_session_allowed()

        market = self.is_market_open(symbol)

        if not market["success"]:

            return market

        checks["market_open"] = (
            market["data"]["market_open"]
        )

        allowed = all(checks.values())

        return {
            "success": allowed,
            "message": (
                "Trading session validated."
                if allowed
                else "Trading blocked by session manager."
            ),
            "data": {
                "allowed": allowed,
                "checks": checks,
                "failed_checks": [
                    k
                    for k, v in checks.items()
                    if not v
                ],
                "trade_mode": market["data"]["trade_mode"],
                "utc_time": self._utc_now().isoformat()
            }
        }


trading_session_manager = TradingSessionManager()