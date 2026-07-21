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
    
    def get_symbol_info(self, symbol):

        status = connector.connect()

        if not status["success"]:
            return status

        info = mt5.symbol_info(symbol)

        if info is None:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Unable to fetch symbol information for {symbol}.",
                    "data": None
            }

        connector.disconnect()

        return {
            "success": True,
            "message": "Symbol information fetched successfully.",
            "data": {
                "symbol": symbol,
                "bid": info.bid,
                "ask": info.ask,
                "spread": info.spread,
                "digits": info.digits,
                "point": info.point,
                "trade_contract_size": info.trade_contract_size,
                "trade_stops_level": info.trade_stops_level,
                "trade_freeze_level": info.trade_freeze_level
           }
        }

    def get_account_info(self):

        status = connector.connect()

        if not status["success"]:
            return status

        account = mt5.account_info()

        if account is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch account information.",
                "data": None
            }

        connector.disconnect()

        return {
            "success": True,
            "message": "Account information fetched successfully.",
            "data": {
                "login": account.login,
                "server": account.server,
                "name": account.name,
                "balance": account.balance,
                "equity": account.equity,
                "margin": account.margin,
                "free_margin": account.margin_free,
                "margin_level": account.margin_level,
                "leverage": account.leverage,
                "currency": account.currency
            }
        }

    def get_positions(self):

        status = connector.connect()

        if not status["success"]:
            return status

        positions = mt5.positions_get()

        if positions is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch open positions.",
                "data": None
            }

        data = []

        for position in positions:

            data.append({
                "ticket": position.ticket,
                "symbol": position.symbol,
                "type": "BUY" if position.type == mt5.POSITION_TYPE_BUY else "SELL",
                "volume": position.volume,
                "price_open": position.price_open,
                "price_current": position.price_current,
                "sl": position.sl,
                "tp": position.tp,
                "profit": position.profit,
                "swap": position.swap,
                "magic": position.magic,
                "comment": position.comment,
                "time": position.time
            })

        connector.disconnect()

        return {
            "success": True,
            "message": f"{len(data)} open position(s) found.",
            "data": data
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
