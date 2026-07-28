from .base_strategy import BaseStrategy
from indicators import indicator_service


class EmaCrossoverStrategy(BaseStrategy):

    def generate_signal(self, symbol, timeframe):

        ema20 = indicator_service.ema(
            symbol,
            timeframe,
            20
        )

        ema50 = indicator_service.ema(
            symbol,
            timeframe,
            50
        )

        if not ema20["success"]:
            return ema20

        if not ema50["success"]:
            return ema50

        ema20_value = ema20["data"]["ema"]
        ema50_value = ema50["data"]["ema"]

        signal = "HOLD"
        confidence = 50
        reason = "EMA values are equal."

        if ema20_value > ema50_value:

            signal = "BUY"
            confidence = 80
            reason = "EMA 20 is above EMA 50."

        elif ema20_value < ema50_value:

            signal = "SELL"
            confidence = 80
            reason = "EMA 20 is below EMA 50."

        return {
            "success": True,
            "data": {
                "strategy": "EMA_CROSSOVER",
                "signal": signal,
                "confidence": confidence,
                "reason": reason,
                "ema20": ema20_value,
                "ema50": ema50_value
            }
        }