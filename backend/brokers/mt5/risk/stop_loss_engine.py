from indicators import indicator_service
from market import market_service


class StopLossEngine:

    DEFAULT_MULTIPLIER = 2

    def atr_stop_loss(
        self,
        symbol,
        timeframe,
        direction,
        multiplier=None
    ):

        if multiplier is None:
            multiplier = self.DEFAULT_MULTIPLIER

        tick = market_service.get_tick(symbol)

        if not tick["success"]:
            return tick

        atr = indicator_service.atr(
            symbol,
            timeframe,
            14
        )

        if not atr["success"]:
            return atr

        current_price = tick["data"]["ask"]

        atr_value = atr["data"]["atr"]

        distance = atr_value * multiplier

        if direction.upper() == "BUY":

            stop_loss = current_price - distance

        else:

            stop_loss = current_price + distance

        pip_size = 0.0001

        if "JPY" in symbol.upper():
            pip_size = 0.01

        distance_pips = distance / pip_size

        return {
            "success": True,
            "message": "ATR Stop Loss calculated successfully.",
            "data": {
                "method": "ATR",
                "symbol": symbol,
                "timeframe": timeframe,
                "direction": direction.upper(),
                "entry_price": round(current_price, 5),
                "stop_loss": round(stop_loss, 5),
                "atr": round(atr_value, 5),
                "multiplier": multiplier,
                "distance": round(distance, 5),
                "distance_pips": round(distance_pips, 1)
            }
        }


stop_loss_engine = StopLossEngine()