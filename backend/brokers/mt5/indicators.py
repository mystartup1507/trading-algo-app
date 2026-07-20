import pandas as pd
import numpy as np
import json
import os
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
        atr_values = self._calculate_atr(df, period)

        atr = atr_values[-1]
        
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

    def _calculate_atr(self, df, period):

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

        atr_values = [None] * period

        atr_values.append(atr)

        for tr in true_ranges[period:]:

            atr = ((atr * (period - 1)) + tr) / period

            atr_values.append(atr)

        return atr_values

    def supertrend(self, symbol, timeframe, period, multiplier):

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

        atr_values = self._calculate_atr(df, period)

        df["atr"] = atr_values
        
        df = df.dropna().reset_index(drop=True)

        df["hl2"] = (df["high"] + df["low"]) / 2

        df["basic_upper_band"] = (
            df["hl2"] + (multiplier * df["atr"])
        )

        df["basic_lower_band"] = (
            df["hl2"] - (multiplier * df["atr"])
        )
        final_upper_band = []
        final_lower_band = []

        for i in range(len(df)):

            if i == 0:
                final_upper_band.append(df["basic_upper_band"].iloc[i])
                final_lower_band.append(df["basic_lower_band"].iloc[i])
                continue

            previous_close = df["close"].iloc[i - 1]

            current_upper = df["basic_upper_band"].iloc[i]
            previous_upper = final_upper_band[i - 1]

            if (
                current_upper < previous_upper
                or previous_close > previous_upper
            ):
                final_upper_band.append(current_upper)
            else:
                final_upper_band.append(previous_upper)

            current_lower = df["basic_lower_band"].iloc[i]
            previous_lower = final_lower_band[i - 1]

            if (
                current_lower > previous_lower
                or previous_close < previous_lower
            ):
                final_lower_band.append(current_lower)
            else:
                final_lower_band.append(previous_lower)

        df["final_upper_band"] = final_upper_band
        df["final_lower_band"] = final_lower_band 
   
        supertrend = []
        trend = []

        for i in range(len(df)):

            if i == 0:

                if df["close"].iloc[i] >= final_lower_band[i]:
                      supertrend.append(final_lower_band[i])
                      trend.append("BUY")
                else:
                      supertrend.append(final_upper_band[i])
                      trend.append("SELL")

                continue

            previous_supertrend = supertrend[i - 1]

            current_close = df["close"].iloc[i]
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            if previous_supertrend == final_upper_band[i - 1]:

                if current_high <= final_upper_band[i]:
                    supertrend.append(final_upper_band[i])
                    trend.append("SELL")
                else:
                    supertrend.append(final_lower_band[i])
                    trend.append("BUY")

            else:

                if current_low >= final_lower_band[i]:
                    supertrend.append(final_lower_band[i])
                    trend.append("BUY")
                else:
                    supertrend.append(final_upper_band[i])
                    trend.append("SELL")

        df["supertrend"] = supertrend
        df["trend"] = trend

        latest = df.iloc[-1]

        return {
            "success": True,
            "message": "Supertrend calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "multiplier": multiplier,
                "trend": latest["trend"],
                "supertrend": round(float(latest["supertrend"]), 5)
            }
        }

    def macd(self, symbol, timeframe):
        
    

        candles = market_service.get_candles(
            symbol,
            timeframe,
            200
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(candles["data"])

        close = df["close"]

        ema_fast = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema_slow = close.ewm(
            span=26,
            adjust=False
        ).mean()

        macd_line = ema_fast - ema_slow

        signal_line = macd_line.ewm(
            span=9,
            adjust=False
        ).mean()

        histogram = macd_line - signal_line

        return {
            "success": True,
            "message": "MACD calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "macd": round(float(macd_line.iloc[-1]), 5),
                "signal": round(float(signal_line.iloc[-1]), 5),
                "histogram": round(float(histogram.iloc[-1]), 5)
            }
        }

    def adx(self, symbol, timeframe, period=14):

        json_path = os.getenv("MT5_ADX_FILE")
  
        if not json_path:
        return {
            "success": False,
            "message": "MT5_ADX_FILE environment variable is not configured."
        }

        if not os.path.exists(json_path):
            return {
                "success": False,
                "message": "adx.json not found. Please ensure the MT5 Bridge EA is running."
            }

        try:
            with open(json_path, "r", encoding="utf-16") as f:
                content = f.read().strip()

            if not content:
                return {
                    "success": False,
                    "message": "adx.json is empty. MT5 is updating the file. Please try again."
                }

            data = json.loads(content)

            return {
                "success": True,
                "message": "ADX loaded from MT5 Bridge.",
                "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "adx": float(data["adx"]),
                "+di": float(data["plus_di"]),
                "-di": float(data["minus_di"])
            }
        }

        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }

indicator_service = MT5Indicators()
