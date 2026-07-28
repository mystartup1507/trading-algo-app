from .base_strategy import BaseStrategy
from indicators import indicator_service


class BollingerStrategy(BaseStrategy):

    def generate_signal(
        self,
        symbol,
        timeframe,
        period=20,
        deviation=2
    ):

        result = indicator_service.bollinger_bands(
            symbol,
            timeframe,
            period,
            deviation
        )

        if not result["success"]:
            return result

        data = result["data"]

        current_price = data["middle_band"]  # temporary default
        lower_band = data["lower_band"]
        middle_band = data["middle_band"]
        upper_band = data["upper_band"]

        # If your indicator returns current_price, use it
        if "current_price" in data:
            current_price = data["current_price"]

        signal = "HOLD"
        confidence = 60
        reason = "Price is inside Bollinger Bands."

        if current_price <= lower_band:

            signal = "BUY"
            confidence = 85
            reason = "Price touched the Lower Bollinger Band."

        elif current_price >= upper_band:

            signal = "SELL"
            confidence = 85
            reason = "Price touched the Upper Bollinger Band."

        return {
            "success": True,
            "data": {
                "strategy": "BOLLINGER_BANDS",
                "signal": signal,
                "confidence": confidence,
                "reason": reason,
                "current_price": current_price,
                "lower_band": lower_band,
                "middle_band": middle_band,
                "upper_band": upper_band
            }
        }