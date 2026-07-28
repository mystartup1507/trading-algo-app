class TakeProfitEngine:

    DEFAULT_RR = 2.0

    def calculate(
        self,
        entry_price,
        stop_loss,
        direction,
        risk_reward=None
    ):

        if risk_reward is None:
            risk_reward = self.DEFAULT_RR

        direction = direction.upper()

        if direction == "BUY":

            risk = entry_price - stop_loss

            take_profit = (
                entry_price
                + (risk * risk_reward)
            )

        elif direction == "SELL":

            risk = stop_loss - entry_price

            take_profit = (
                entry_price
                - (risk * risk_reward)
            )

        else:

            return {
                "success": False,
                "message": "Invalid direction."
            }

        return {
            "success": True,
            "message": "Take Profit calculated successfully.",
            "data": {
                "method": "RISK_REWARD",
                "direction": direction,
                "entry_price": round(entry_price, 5),
                "stop_loss": round(stop_loss, 5),
                "risk": round(risk, 5),
                "risk_reward": risk_reward,
                "take_profit": round(take_profit, 5)
            }
        }


take_profit_engine = TakeProfitEngine()