from .base_strategy import BaseStrategy
from indicators import indicator_service


class IchimokuStrategy(BaseStrategy):

    def generate_signal(self, symbol, timeframe):

        result = indicator_service.ichimoku(
            symbol,
            timeframe
        )

        if not result["success"]:
            return result

        data = result["data"]

        tenkan = data["tenkan"]
        kijun = data["kijun"]
        senkou_a = data["senkou_a"]
        senkou_b = data["senkou_b"]
        chikou = data["chikou"]

        signal = "HOLD"
        confidence = 60
        reason = "Mixed Ichimoku signals."

        if (
            tenkan > kijun
            and chikou > senkou_a
            and senkou_a > senkou_b
        ):

            signal = "BUY"
            confidence = 90
            reason = "Bullish Ichimoku Cloud."

        elif (
            tenkan < kijun
            and chikou < senkou_a
            and senkou_a < senkou_b
        ):

            signal = "SELL"
            confidence = 90
            reason = "Bearish Ichimoku Cloud."

        return {
            "success": True,
            "data": {
                "strategy": "ICHIMOKU",
                "signal": signal,
                "confidence": confidence,
                "reason": reason,
                "tenkan": tenkan,
                "kijun": kijun,
                "senkou_a": senkou_a,
                "senkou_b": senkou_b,
                "chikou": chikou
            }
        }