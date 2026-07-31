class LiveExecutionGuard:

    # Live trading remains disabled by default.
    LIVE_TRADING_ENABLED = False

    # Explicit confirmation required for live execution.
    CONFIRMATION_TOKEN = "CONFIRM_LIVE_TRADE"

    def validate(
        self,
        symbol,
        direction,
        lot_size,
        confirmation_token=None
    ):

        checks = {}

        # ---------------------------------
        # Master live-trading switch
        # ---------------------------------

        checks["live_trading_enabled"] = (
            self.LIVE_TRADING_ENABLED is True
        )

        # ---------------------------------
        # Confirmation token
        # ---------------------------------

        checks["confirmation_token"] = (
            confirmation_token
            == self.CONFIRMATION_TOKEN
        )

        # ---------------------------------
        # Symbol
        # ---------------------------------

        checks["symbol"] = (
            symbol is not None
            and str(symbol).strip() != ""
        )

        # ---------------------------------
        # Direction
        # ---------------------------------

        direction = (
            str(direction).upper().strip()
            if direction is not None
            else ""
        )

        checks["direction"] = (
            direction in ["BUY", "SELL"]
        )

        # ---------------------------------
        # Lot size
        # ---------------------------------

        try:

            volume = float(lot_size)

            checks["lot_size"] = (
                volume > 0
            )

        except (TypeError, ValueError):

            checks["lot_size"] = False

        # ---------------------------------
        # Final result
        # ---------------------------------

        valid = all(checks.values())

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        if not valid:

            return {
                "success": False,
                "message": (
                    "Live execution blocked by "
                    "execution safety guard."
                ),
                "data": {
                    "allowed": False,
                    "checks": checks,
                    "failed_checks": failed_checks
                }
            }

        return {
            "success": True,
            "message": (
                "Live execution safety checks passed."
            ),
            "data": {
                "allowed": True,
                "checks": checks,
                "failed_checks": []
            }
        }


live_execution_guard = LiveExecutionGuard()