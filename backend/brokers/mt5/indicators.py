import pandas as pd
from market import market_service


class MT5Indicators:

    def ema(self, symbol, timeframe, period):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            period * 3
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(candles["data"])

        df["ema"] = df["close"].ewm(
            span=period,
            adjust=False
        ).mean()

        return {
            "success": True,
            "message": "EMA calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "ema": float(df["ema"].iloc[-1])
            }
        }


indicator_service = MT5Indicators()