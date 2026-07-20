import MetaTrader5 as mt5
from connector import connector


class MT5Market:

    def get_symbols(self):

        status = connector.connect()

        if not status["success"]:
            return status

        symbols = mt5.symbols_get()

        if symbols is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch symbols.",
                "data": None
            }

        symbol_list = []

        for symbol in symbols:

            symbol_list.append(symbol.name)

        connector.disconnect()

        return {
            "success": True,
            "message": f"{len(symbol_list)} symbols loaded.",
            "data": symbol_list
        }


    def get_tick(self, symbol):

        status = connector.connect()

        if not status["success"]:
            return status

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Unable to fetch live tick for {symbol}.",
                "data": None
            }

        connector.disconnect()

        return {
            "success": True,
            "message": "Live market data fetched successfully.",
            "data": {
                "symbol": symbol,
                "bid": tick.bid,
                "ask": tick.ask,
                "last": tick.last,
                "time": tick.time
            }
        }

    def get_candles(self, symbol, timeframe, count):

        status = connector.connect()

        if not status["success"]:
            return status

        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1
        }

        if timeframe not in timeframe_map:

            connector.disconnect()

            return {
                "success": False,
                "message": "Invalid timeframe.",
                "data": None
            }

        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe_map[timeframe],
            1,
            int(count)
        )

        if rates is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch candle data.",
                "data": None
            }

        candles = []

        for rate in rates:

            candles.append({
                "time": int(rate["time"]),
                "open": float(rate["open"]),
                "high": float(rate["high"]),
                "low": float(rate["low"]),
                "close": float(rate["close"]),
                "tick_volume": int(rate["tick_volume"])
            })

        connector.disconnect()

        return {
            "success": True,
            "message": f"{len(candles)} candles loaded.",
            "data": candles
        }

market_service = MT5Market()
