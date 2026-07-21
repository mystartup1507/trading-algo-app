from .base_strategy import BaseStrategy
from config.strategy_config import StrategyConfig


class EmaRsiAdxStrategy(BaseStrategy):

    def __init__(self):
        self.config = StrategyConfig()

    def generate_signal(self, snapshot):

    #
    # Default
    #
        snapshot.signal = "HOLD"
        snapshot.reason = "No valid trading setup."

    #
    # BUY
    #
        if (
            snapshot.trend.state == "UPTREND"
            and snapshot.momentum.state == "STRONG"
            and snapshot.volatility.state == "NORMAL"
        ):

            snapshot.signal = "BUY"
            snapshot.reason = (
                "Trend and Momentum are bullish."
            )

    #
    # SELL
    #
        elif (
            snapshot.trend.state == "DOWNTREND"
            and snapshot.momentum.state == "STRONG"
            and snapshot.volatility.state == "NORMAL"
        ):

            snapshot.signal = "SELL"
            snapshot.reason = (
                "Trend and Momentum are bearish."
            )

        return {
            "success": True,
            "message": self.config.STRATEGY_NAME,
            "data": {
                "signal": snapshot.signal,
                "reason": snapshot.reason,
                "trend": snapshot.trend.state,
                "momentum": snapshot.momentum.state,
                "confidence": (
                    snapshot.trend.confidence
                    * snapshot.momentum.confidence
                ) ** 0.5
            }
        }