from datetime import datetime, timedelta, timezone


class TradeCooldownManager:

    # =====================================================
    # Cooldown after every executed trade
    # =====================================================

    COOLDOWN_MINUTES = 15

    def __init__(self):

        self._last_trade_time = None

    # =====================================================

    def record_trade(self):

        self._last_trade_time = datetime.now(
            timezone.utc
        )

    # =====================================================

    def reset(self):

        self._last_trade_time = None

    # =====================================================

    def status(self):

        return {
            "last_trade_time": (
                self._last_trade_time.isoformat()
                if self._last_trade_time
                else None
            ),
            "cooldown_minutes": self.COOLDOWN_MINUTES
        }

    # =====================================================

    def validate(self):

        if self._last_trade_time is None:

            return {
                "success": True,
                "message": "Cooldown not active.",
                "data": {
                    "allowed": True,
                    "remaining_seconds": 0
                }
            }

        elapsed = (
            datetime.now(timezone.utc)
            - self._last_trade_time
        )

        cooldown = timedelta(
            minutes=self.COOLDOWN_MINUTES
        )

        if elapsed >= cooldown:

            return {
                "success": True,
                "message": "Cooldown expired.",
                "data": {
                    "allowed": True,
                    "remaining_seconds": 0
                }
            }

        remaining = int(
            (cooldown - elapsed).total_seconds()
        )

        return {
            "success": False,
            "message": "Trade cooldown active.",
            "data": {
                "allowed": False,
                "remaining_seconds": remaining,
                "last_trade_time": (
                    self._last_trade_time.isoformat()
                )
            }
        }


trade_cooldown_manager = TradeCooldownManager()