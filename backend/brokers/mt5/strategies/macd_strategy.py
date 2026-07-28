from .base_strategy import BaseStrategy
from indicators import indicator_service


class MacdStrategy(BaseStrategy):

    def generate_signal(self, symbol, timeframe):

        result = indicator_service.macd(
            symbol,
            timeframe
        )

        if not result["success"]:
            return result

        macd = result["data"]["macd"]
        signal_line = result["data"]["signal"]

        signal = "HOLD"
        confidence = 50
        reason = "MACD equals Signal."

        if macd > signal_line:

            signal = "BUY"
            confidence = 80
            reason = "MACD is above Signal."

        elif macd < signal_line:

            signal = "SELL"
            confidence = 80
            reason = "MACD is below Signal."

        return {
            "success": True,
            "data": {
                "strategy": "MACD",
                "signal": signal,
                "confidence": confidence,
                "reason": reason,
                "macd": macd,
                "signal_line": signal_line
            }
        }