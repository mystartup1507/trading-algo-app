class TradeValidator:

    MIN_RISK_REWARD = 1.5

    def validate(
        self,
        direction,
        entry_price,
        stop_loss,
        take_profit,
        lot_size
    ):

        direction = direction.upper()

        checks = {}

        #
        # Direction
        #
        checks["direction"] = (
            direction in ["BUY", "SELL"]
        )

        #
        # Lot Size
        #
        checks["lot_size"] = (
            lot_size > 0
        )

        #
        # Stop Loss
        #
        if direction == "BUY":

            checks["stop_loss"] = (
                stop_loss < entry_price
            )

        elif direction == "SELL":

            checks["stop_loss"] = (
                stop_loss > entry_price
            )

        else:

            checks["stop_loss"] = False

        #
        # Take Profit
        #
        if direction == "BUY":

            checks["take_profit"] = (
                take_profit > entry_price
            )

        elif direction == "SELL":

            checks["take_profit"] = (
                take_profit < entry_price
            )

        else:

            checks["take_profit"] = False

        #
        # Risk Reward
        #
        risk = abs(entry_price - stop_loss)

        reward = abs(take_profit - entry_price)

        if risk > 0:

            rr = reward / risk

        else:

            rr = 0

        checks["risk_reward"] = (
            rr >= self.MIN_RISK_REWARD
        )

        valid = all(checks.values())

        failed_checks = [
            key
            for key, value in checks.items()
            if not value
        ]

        return {
            "success": valid,
            "message": (
                "Trade validation passed."
                if valid
                else "Trade validation failed."
            ),
            "data": {
                "valid": valid,
                "risk_reward": round(rr, 2),
                "checks": checks,
                "failed_checks": failed_checks
            }
        }


trade_validator = TradeValidator()