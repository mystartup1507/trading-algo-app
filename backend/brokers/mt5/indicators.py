import pandas as pd
import numpy as np

from market import market_service
from execution import execution_service


class MT5Indicators:

    def account_info(self):

        return market_service.get_account_info()

    def positions(self):

        return market_service.get_positions()

    def order_history(self):

        return market_service.get_order_history()

    def market_order(
        self,
        symbol,
        volume,
        order_type,
        sl=0.0,
        tp=0.0,
        comment="JD-Algo",
        magic=1001
    ):

        return execution_service.market_order(
            symbol,
            volume,
            order_type,
            sl,
            tp,
            comment,
            magic
        )

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

    def close_position(self, ticket):

        return execution_service.close_position(ticket)

    def modify_position(self, ticket, sl=None, tp=None):

        return execution_service.modify_position(
            ticket,
            sl,
            tp
        )

    def pending_order(
        self,
        symbol,
        volume,
        order_type,
        price,
        sl=0.0,
        tp=0.0,
        comment="JD-Algo Pending",
        magic=1001
    ):

        return execution_service.pending_order(
            symbol,
            volume,
            order_type,
            price,
            sl,
            tp,
            comment,
            magic
        )

    def get_pending_orders(self):

        return execution_service.get_pending_orders()

    def get_pending_order(self, ticket):

        return execution_service.get_pending_order(ticket)

    def modify_pending_order(
        self,
        ticket,
        price,
        sl=None,
        tp=None
    ):

        return execution_service.modify_pending_order(
            ticket,
            price,
            sl,
            tp
        )

    def cancel_pending_order(self, ticket):

        return execution_service.cancel_pending_order(
            ticket
        )

    def close_positions_by_symbol(self, symbol):

        return execution_service.close_positions_by_symbol(
            symbol
        )

    def close_all_positions(self):

        return execution_service.close_all_positions()

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

            change = (
                closes[i] -
                closes[i - 1]
            )

            if change > 0:

                gains.append(change)
                losses.append(0.0)

            else:

                gains.append(0.0)
                losses.append(abs(change))

        avg_gain = (
            sum(gains[:period]) /
            period
        )

        avg_loss = (
            sum(losses[:period]) /
            period
        )

        rsi_values = []

        for i in range(
            period,
            len(gains)
        ):

            avg_gain = (
                (
                    avg_gain *
                    (period - 1)
                ) +
                gains[i]
            ) / period

            avg_loss = (
                (
                    avg_loss *
                    (period - 1)
                ) +
                losses[i]
            ) / period

            if avg_loss == 0:

                rsi = 100.0

            else:

                rs = (
                    avg_gain /
                    avg_loss
                )

                rsi = (
                    100 -
                    (
                        100 /
                        (1 + rs)
                    )
                )

            rsi_values.append(rsi)

        return {
            "success": True,
            "message": "RSI calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "rsi": round(
                    rsi_values[-1],
                    2
                )
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

        atr_values = self._calculate_atr(
            df,
            period
        )

        atr = atr_values[-1]

        return {
            "success": True,
            "message": "ATR calculated successfully.",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "atr": round(
                    atr,
                    5
                )
            }
        }

    def _calculate_atr(self, df, period):

        high = df["high"].tolist()
        low = df["low"].tolist()
        close = df["close"].tolist()

        true_ranges = []

        for i in range(
            1,
            len(df)
        ):

            tr = max(
                high[i] - low[i],
                abs(
                    high[i] -
                    close[i - 1]
                ),
                abs(
                    low[i] -
                    close[i - 1]
                )
            )

            true_ranges.append(tr)

        atr = (
            sum(
                true_ranges[:period]
            ) /
            period
        )

        atr_values = (
            [None] * period
        )

        atr_values.append(atr)

        for tr in true_ranges[period:]:

            atr = (
                (
                    atr *
                    (period - 1)
                ) +
                tr
            ) / period

            atr_values.append(atr)

        return atr_values

    def supertrend(
        self,
        symbol,
        timeframe,
        period,
        multiplier
    ):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            max(period + 100, 200)
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(
            candles["data"]
        )

        if len(df) <= period:

            return {
                "success": False,
                "message": "Not enough candle data.",
                "data": None
            }

        atr_values = self._calculate_atr(
            df,
            period
        )

        df["atr"] = atr_values

        df = (
            df
            .dropna()
            .reset_index(drop=True)
        )

        df["hl2"] = (
            df["high"] +
            df["low"]
        ) / 2

        df["basic_upper_band"] = (
            df["hl2"] +
            (
                multiplier *
                df["atr"]
            )
        )

        df["basic_lower_band"] = (
            df["hl2"] -
            (
                multiplier *
                df["atr"]
            )
        )

        final_upper_band = []
        final_lower_band = []

        for i in range(len(df)):

            if i == 0:

                final_upper_band.append(
                    df[
                        "basic_upper_band"
                    ].iloc[i]
                )

                final_lower_band.append(
                    df[
                        "basic_lower_band"
                    ].iloc[i]
                )

                continue

            previous_close = (
                df["close"].iloc[i - 1]
            )

            current_upper = (
                df[
                    "basic_upper_band"
                ].iloc[i]
            )

            previous_upper = (
                final_upper_band[i - 1]
            )

            if (
                current_upper <
                previous_upper
                or
                previous_close >
                previous_upper
            ):

                final_upper_band.append(
                    current_upper
                )

            else:

                final_upper_band.append(
                    previous_upper
                )

            current_lower = (
                df[
                    "basic_lower_band"
                ].iloc[i]
            )

            previous_lower = (
                final_lower_band[i - 1]
            )

            if (
                current_lower >
                previous_lower
                or
                previous_close <
                previous_lower
            ):

                final_lower_band.append(
                    current_lower
                )

            else:

                final_lower_band.append(
                    previous_lower
                )

        df["final_upper_band"] = (
            final_upper_band
        )

        df["final_lower_band"] = (
            final_lower_band
        )

        supertrend = []
        trend = []

        for i in range(len(df)):

            if i == 0:

                if (
                    df["close"].iloc[i] >=
                    final_lower_band[i]
                ):

                    supertrend.append(
                        final_lower_band[i]
                    )

                    trend.append("BUY")

                else:

                    supertrend.append(
                        final_upper_band[i]
                    )

                    trend.append("SELL")

                continue

            previous_supertrend = (
                supertrend[i - 1]
            )

            current_high = (
                df["high"].iloc[i]
            )

            current_low = (
                df["low"].iloc[i]
            )

            if (
                previous_supertrend ==
                final_upper_band[i - 1]
            ):

                if (
                    current_high <=
                    final_upper_band[i]
                ):

                    supertrend.append(
                        final_upper_band[i]
                    )

                    trend.append("SELL")

                else:

                    supertrend.append(
                        final_lower_band[i]
                    )

                    trend.append("BUY")

            else:

                if (
                    current_low >=
                    final_lower_band[i]
                ):

                    supertrend.append(
                        final_lower_band[i]
                    )

                    trend.append("BUY")

                else:

                    supertrend.append(
                        final_upper_band[i]
                    )

                    trend.append("SELL")

        df["supertrend"] = supertrend
        df["trend"] = trend

        latest = df.iloc[-1]

        return {
            "success": True,
            "message": (
                "Supertrend calculated "
                "successfully."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "multiplier": multiplier,
                "trend": latest["trend"],
                "supertrend": round(
                    float(
                        latest[
                            "supertrend"
                        ]
                    ),
                    5
                )
            }
        }

    def bollinger_bands(
        self,
        symbol,
        timeframe,
        period=20,
        deviation=2
    ):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            max(period + 100, 200)
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(
            candles["data"]
        )

        if len(df) < period:

            return {
                "success": False,
                "message": "Not enough candle data.",
                "data": None
            }

        df["middle_band"] = (
            df["close"]
            .rolling(period)
            .mean()
        )

        std = (
            df["close"]
            .rolling(period)
            .std()
        )

        df["upper_band"] = (
            df["middle_band"] +
            (
                std *
                deviation
            )
        )

        df["lower_band"] = (
            df["middle_band"] -
            (
                std *
                deviation
            )
        )

        latest = df.iloc[-1]

        return {
            "success": True,
            "message": (
                "Bollinger Bands calculated "
                "successfully."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period": period,
                "deviation": deviation,
                "upper_band": round(
                    float(
                        latest[
                            "upper_band"
                        ]
                    ),
                    5
                ),
                "middle_band": round(
                    float(
                        latest[
                            "middle_band"
                        ]
                    ),
                    5
                ),
                "lower_band": round(
                    float(
                        latest[
                            "lower_band"
                        ]
                    ),
                    5
                )
            }
        }

    def vwap(self, symbol, timeframe):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            200
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(
            candles["data"]
        )

        if len(df) == 0:

            return {
                "success": False,
                "message": "No candle data found.",
                "data": None
            }

        df["tp"] = (
            df["high"] +
            df["low"] +
            df["close"]
        ) / 3

        df["tpv"] = (
            df["tp"] *
            df["tick_volume"]
        )

        cumulative_volume = (
            df["tick_volume"]
            .cumsum()
        )

        if (
            cumulative_volume.iloc[-1] ==
            0
        ):

            return {
                "success": False,
                "message": (
                    "Cannot calculate VWAP "
                    "because cumulative volume "
                    "is zero."
                ),
                "data": None
            }

        df["vwap"] = (
            df["tpv"].cumsum() /
            cumulative_volume
        )

        latest = df.iloc[-1]

        return {
            "success": True,
            "message": (
                "VWAP calculated successfully."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "vwap": round(
                    float(
                        latest["vwap"]
                    ),
                    5
                ),
                "current_price": round(
                    float(
                        latest["close"]
                    ),
                    5
                )
            }
        }

    def ichimoku(
        self,
        symbol,
        timeframe
    ):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            200
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(
            candles["data"]
        )

        if len(df) < 52:

            return {
                "success": False,
                "message": "Not enough candle data.",
                "data": None
            }

        tenkan_high = (
            df["high"]
            .rolling(9)
            .max()
        )

        tenkan_low = (
            df["low"]
            .rolling(9)
            .min()
        )

        df["tenkan"] = (
            tenkan_high +
            tenkan_low
        ) / 2

        kijun_high = (
            df["high"]
            .rolling(26)
            .max()
        )

        kijun_low = (
            df["low"]
            .rolling(26)
            .min()
        )

        df["kijun"] = (
            kijun_high +
            kijun_low
        ) / 2

        df["senkou_a"] = (
            (
                df["tenkan"] +
                df["kijun"]
            ) /
            2
        ).shift(26)

        spanb_high = (
            df["high"]
            .rolling(52)
            .max()
        )

        spanb_low = (
            df["low"]
            .rolling(52)
            .min()
        )

        df["senkou_b"] = (
            (
                spanb_high +
                spanb_low
            ) /
            2
        ).shift(26)

        df["chikou"] = (
            df["close"]
            .shift(-26)
        )

        latest = df.iloc[-27]

        return {
            "success": True,
            "message": (
                "Ichimoku calculated "
                "successfully."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "tenkan": round(
                    float(
                        latest["tenkan"]
                    ),
                    5
                ),
                "kijun": round(
                    float(
                        latest["kijun"]
                    ),
                    5
                ),
                "senkou_a": round(
                    float(
                        latest["senkou_a"]
                    ),
                    5
                ),
                "senkou_b": round(
                    float(
                        latest["senkou_b"]
                    ),
                    5
                ),
                "chikou": round(
                    float(
                        latest["chikou"]
                    ),
                    5
                )
            }
        }

    def macd(
        self,
        symbol,
        timeframe
    ):

        candles = market_service.get_candles(
            symbol,
            timeframe,
            200
        )

        if not candles["success"]:
            return candles

        df = pd.DataFrame(
            candles["data"]
        )

        close = df["close"]

        ema_fast = close.ewm(
            span=12,
            adjust=False
        ).mean()

        ema_slow = close.ewm(
            span=26,
            adjust=False
        ).mean()

        macd_line = (
            ema_fast -
            ema_slow
        )

        signal_line = (
            macd_line.ewm(
                span=9,
                adjust=False
            ).mean()
        )

        histogram = (
            macd_line -
            signal_line
        )

        return {
            "success": True,
            "message": (
                "MACD calculated successfully."
            ),
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "macd": round(
                    float(
                        macd_line.iloc[-1]
                    ),
                    5
                ),
                "signal": round(
                    float(
                        signal_line.iloc[-1]
                    ),
                    5
                ),
                "histogram": round(
                    float(
                        histogram.iloc[-1]
                    ),
                    5
                )
            }
        }

    def adx(
        self,
        symbol,
        timeframe,
        period=14
    ):

        if (
            not isinstance(period, int)
            or period <= 1
        ):

            return {
                "success": False,
                "message": (
                    "ADX period must be an "
                    "integer greater than 1."
                ),
                "data": None
            }

        candle_count = max(
            period * 10,
            200
        )

        candles = (
            market_service.get_candles(
                symbol,
                timeframe,
                candle_count
            )
        )

        if not candles["success"]:
            return candles

        try:

            df = pd.DataFrame(
                candles["data"]
            )

            required_columns = {
                "high",
                "low",
                "close"
            }

            if not required_columns.issubset(
                df.columns
            ):

                return {
                    "success": False,
                    "message": (
                        "ADX candle data is "
                        "missing high, low or "
                        "close values."
                    ),
                    "data": None
                }

            minimum_candles = (
                (period * 2) + 1
            )

            if len(df) < minimum_candles:

                return {
                    "success": False,
                    "message": (
                        "Not enough candle data "
                        "to calculate ADX."
                    ),
                    "data": {
                        "required": (
                            minimum_candles
                        ),
                        "received": len(df)
                    }
                }

            high = (
                pd.to_numeric(
                    df["high"],
                    errors="coerce"
                )
            )

            low = (
                pd.to_numeric(
                    df["low"],
                    errors="coerce"
                )
            )

            close = (
                pd.to_numeric(
                    df["close"],
                    errors="coerce"
                )
            )

            indicator_df = pd.DataFrame({
                "high": high,
                "low": low,
                "close": close
            }).dropna().reset_index(
                drop=True
            )

            if (
                len(indicator_df) <
                minimum_candles
            ):

                return {
                    "success": False,
                    "message": (
                        "Not enough valid OHLC "
                        "data to calculate ADX."
                    ),
                    "data": None
                }

            high = indicator_df["high"]
            low = indicator_df["low"]
            close = indicator_df["close"]

            previous_high = high.shift(1)
            previous_low = low.shift(1)
            previous_close = close.shift(1)

            up_move = (
                high -
                previous_high
            )

            down_move = (
                previous_low -
                low
            )

            plus_dm = pd.Series(
                np.where(
                    (
                        (up_move > down_move) &
                        (up_move > 0)
                    ),
                    up_move,
                    0.0
                ),
                index=indicator_df.index,
                dtype="float64"
            )

            minus_dm = pd.Series(
                np.where(
                    (
                        (down_move > up_move) &
                        (down_move > 0)
                    ),
                    down_move,
                    0.0
                ),
                index=indicator_df.index,
                dtype="float64"
            )

            true_range = pd.concat(
                [
                    high - low,
                    (
                        high -
                        previous_close
                    ).abs(),
                    (
                        low -
                        previous_close
                    ).abs()
                ],
                axis=1
            ).max(axis=1)

            true_range.iloc[0] = np.nan
            plus_dm.iloc[0] = np.nan
            minus_dm.iloc[0] = np.nan

            atr_smoothed = (
                true_range.ewm(
                    alpha=(1.0 / period),
                    adjust=False,
                    min_periods=period
                ).mean()
            )

            plus_dm_smoothed = (
                plus_dm.ewm(
                    alpha=(1.0 / period),
                    adjust=False,
                    min_periods=period
                ).mean()
            )

            minus_dm_smoothed = (
                minus_dm.ewm(
                    alpha=(1.0 / period),
                    adjust=False,
                    min_periods=period
                ).mean()
            )

            safe_atr = (
                atr_smoothed.replace(
                    0,
                    np.nan
                )
            )

            plus_di = (
                100.0 *
                (
                    plus_dm_smoothed /
                    safe_atr
                )
            )

            minus_di = (
                100.0 *
                (
                    minus_dm_smoothed /
                    safe_atr
                )
            )

            di_sum = (
                plus_di +
                minus_di
            )

            di_difference = (
                plus_di -
                minus_di
            ).abs()

            dx = (
                100.0 *
                (
                    di_difference /
                    di_sum.replace(
                        0,
                        np.nan
                    )
                )
            )

            adx_series = (
                dx.ewm(
                    alpha=(1.0 / period),
                    adjust=False,
                    min_periods=period
                ).mean()
            )

            valid = pd.DataFrame({
                "adx": adx_series,
                "plus_di": plus_di,
                "minus_di": minus_di
            }).replace(
                [np.inf, -np.inf],
                np.nan
            ).dropna()

            if valid.empty:

                return {
                    "success": False,
                    "message": (
                        "ADX calculation did "
                        "not produce a valid "
                        "result."
                    ),
                    "data": None
                }

            latest = valid.iloc[-1]

            return {
                "success": True,
                "message": (
                    "ADX calculated from "
                    "MT5 candle data "
                    "successfully."
                ),
                "data": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "period": period,
                    "adx": round(
                        float(
                            latest["adx"]
                        ),
                        2
                    ),
                    "+di": round(
                        float(
                            latest["plus_di"]
                        ),
                        2
                    ),
                    "-di": round(
                        float(
                            latest["minus_di"]
                        ),
                        2
                    ),
                    "calculation_method": (
                        "WILDER_MT5_CANDLES"
                    )
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "ADX calculation error: "
                    f"{str(error)}"
                ),
                "data": None
            }

    def symbol_info(self, symbol):

        return market_service.get_symbol_info(
            symbol
        )


indicator_service = MT5Indicators()