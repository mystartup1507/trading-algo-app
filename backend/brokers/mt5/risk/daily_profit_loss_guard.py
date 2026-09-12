from datetime import datetime, timezone


class DailyProfitLossGuard:

    MAX_DAILY_PROFIT = 500.0
    MAX_DAILY_LOSS = -300.0

    def __init__(self):

        self._current_day = None
        self._daily_pnl = 0.0

    def _today(self):

        return datetime.now(
            timezone.utc
        ).date()

    def _reset_if_new_day(self):

        today = self._today()

        if self._current_day != today:

            self._current_day = today
            self._daily_pnl = 0.0

    def record_trade(self, profit):

        self._reset_if_new_day()

        self._daily_pnl += float(profit)

    def validate(self):

        self._reset_if_new_day()

        if self._daily_pnl >= self.MAX_DAILY_PROFIT:

            return {
                "success": False,
                "message": "Daily profit target reached.",
                "data": {
                    "allowed": False,
                    "daily_pnl": self._daily_pnl
                }
            }

        if self._daily_pnl <= self.MAX_DAILY_LOSS:

            return {
                "success": False,
                "message": "Daily loss limit reached.",
                "data": {
                    "allowed": False,
                    "daily_pnl": self._daily_pnl
                }
            }

        return {
            "success": True,
            "message": "Daily P/L validation passed.",
            "data": {
                "allowed": True,
                "daily_pnl": self._daily_pnl,
                "profit_limit": self.MAX_DAILY_PROFIT,
                "loss_limit": self.MAX_DAILY_LOSS
            }
        }


daily_profit_loss_guard = DailyProfitLossGuard()