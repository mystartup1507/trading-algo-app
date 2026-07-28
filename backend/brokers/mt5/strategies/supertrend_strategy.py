from .base_strategy import BaseStrategy
from indicators import indicator_service


class SuperTrendStrategy(BaseStrategy):

    def generate_signal(
        self,
        symbol,
        timeframe,
        period=10,
        multiplier=3
    ):

        result = indicator_service.supertrend(
            symbol,
            timeframe,
            period,
            multiplier
        )

        if not result["success"]:
            return result

        trend = result["data"]["trend"]

        signal = "HOLD"
        confidence = 50
        reason = "No trend detected."

        if trend == "BUY":

            signal = "BUY"
            confidence = 85
            reason = "SuperTrend is Bullish."

        elif trend == "SELL":

            signal = "SELL"
            confidence = 85
            reason = "SuperTrend is Bearish."

        return {
            "success": True,
            "data": {
                "strategy": "SUPERTREND",
                "signal": signal,
                "confidence": confidence,
                "reason": reason,
                "trend": trend
            }
        }