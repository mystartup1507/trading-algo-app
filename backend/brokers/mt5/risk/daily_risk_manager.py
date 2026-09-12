from datetime import datetime, timezone


class DailyRiskManager:

    # =====================================================
    # Configuration
    # =====================================================

    MAX_TRADES_PER_DAY = 10

    def __init__(self):

        self._current_day = None
        self._trade_count = 0

    # =====================================================

    def _today(self):

        return datetime.now(
            timezone.utc
        ).date()

    # =====================================================

    def _reset_if_new_day(self):

        today = self._today()

        if self._current_day != today:

            self._current_day = today
            self._trade_count = 0

    # =====================================================

    def record_trade(self):

        self._reset_if_new_day()

        self._trade_count += 1

    # =====================================================

    def reset(self):

        self._current_day = self._today()
        self._trade_count = 0

    # =====================================================

    def status(self):

        self._reset_if_new_day()

        return {
            "date": str(self._current_day),
            "trade_count": self._trade_count,
            "maximum_trades": self.MAX_TRADES_PER_DAY
        }

    # =====================================================

    def validate(self):

        self._reset_if_new_day()

        if self._trade_count >= self.MAX_TRADES_PER_DAY:

            return {
                "success": False,
                "message": "Daily trade limit reached.",
                "data": {
                    "allowed": False,
                    "trade_count": self._trade_count,
                    "maximum_trades": self.MAX_TRADES_PER_DAY
                }
            }

        return {
            "success": True,
            "message": "Daily risk validation passed.",
            "data": {
                "allowed": True,
                "trade_count": self._trade_count,
                "maximum_trades": self.MAX_TRADES_PER_DAY,
                "remaining_trades": (
                    self.MAX_TRADES_PER_DAY
                    - self._trade_count
                )
            }
        }


daily_risk_manager = DailyRiskManager()