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

    
    def rsi(self, symbol, timeframe, period):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            max(period + 100, 200)
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(candles["data"])

        closes = df["close"].tolist()

        if len(closes) <= period:
            return {
                "success": False,
                "message": "Not enough candle data.",
                "data": None
            }

        gains = []
        losses = []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i - 1]

            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = []

        for i in range(period, len(gains)):

            avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
            avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return {
            "success": True,
            "message": "RSI calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "rsi": round(rsi_values[-1], 2)
            }
        }

    def atr(self, symbol, timeframe, period):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            max(period + 100, 200)
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(candles["data"])

        if len(df) <= period:
            return {
                "success": False,
                "message": "Not enough candle data.",
                "data": None
            }

        high = df["high"].tolist()
        low = df["low"].tolist()
        close = df["close"].tolist()

        true_ranges = []

        for i in range(1, len(df)):

            tr = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )

            true_ranges.append(tr)

        atr = sum(true_ranges[:period]) / period

        for tr in true_ranges[period:]:

            atr = ((atr * (period - 1)) + tr) / period

        return {
            "success": True,
            "message": "ATR calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "atr": round(atr, 5)
            }
        }
      


indicator_service = MT5Indicators()