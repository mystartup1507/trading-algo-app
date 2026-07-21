import MetaTrader5 as mt5
from connector import connector

class MT5Execution:

    def get_filling_mode(self, symbol):

        info = mt5.symbol_info(symbol)

        if info is None:
            return mt5.ORDER_FILLING_IOC

        filling_mode = info.filling_mode

        if filling_mode == mt5.ORDER_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK

        if filling_mode == mt5.ORDER_FILLING_RETURN:
            return mt5.ORDER_FILLING_RETURN

        return mt5.ORDER_FILLING_IOC

    def validate_order(self, symbol, volume):

        status = connector.connect()

        if not status["success"]:
            return status

        info = mt5.symbol_info(symbol)

        if info is None:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Symbol '{symbol}' not found."
            }

    # Automatically make the symbol visible
        if not info.visible:

            if not mt5.symbol_select(symbol, True):

                connector.disconnect()

                return {
                    "success": False,
                    "message": f"Unable to select symbol '{symbol}'."
                }

    # Trading allowed?
        

        volume = float(volume)

    # Minimum lot
        if volume < info.volume_min:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Minimum lot size is {info.volume_min}."
            }

    # Maximum lot
        if volume > info.volume_max:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Maximum lot size is {info.volume_max}."
            }

    # Volume step
        step = info.volume_step

        remainder = round((volume / step) % 1, 8)

        if remainder != 0:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Lot size must be a multiple of {step}."
            }

        connector.disconnect()

        return {
            "success": True,
            "message": "Order validation successful.",
            "data": {
                "volume_min": info.volume_min,
                "volume_max": info.volume_max,
                "volume_step": info.volume_step
            }
        }

    def send_market_order(self, request):

        filling_modes = [
            mt5.ORDER_FILLING_RETURN,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_FOK
        ]

        last_result = None

        for filling_mode in filling_modes:

            request["type_filling"] = filling_mode

            result = mt5.order_send(request)

            if result is None:
                continue

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                return result

            if result.retcode == mt5.TRADE_RETCODE_INVALID_FILL:
                last_result = result
                continue

            return result

        return last_result

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
     #
     # Validate Order
     #
        validation = self.validate_order(symbol, volume)
 
        if not validation["success"]:
            return validation
     

    # Connect
        status = connector.connect()

        if not status["success"]:
            return status

    # Select symbol
        info = mt5.symbol_info(symbol)

        if info is None:

            connector.disconnect()

            return {
                "success": False,
                "message": f"Symbol '{symbol}' not found."
            }

        if not info.visible:

            if not mt5.symbol_select(symbol, True):

                connector.disconnect()

                return {
                    "success": False,
                    "message": f"Unable to select symbol '{symbol}'."
                }

    # Get live tick
        tick = mt5.symbol_info_tick(symbol)

        if tick is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch live price."
            }

        if order_type.upper() == "BUY":
            mt5_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        elif order_type.upper() == "SELL":
            mt5_type = mt5.ORDER_TYPE_SELL
            price = tick.bid

        else:

            connector.disconnect()

            return {
                "success": False,
                "message": "Invalid order type."
            }

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": mt5_type,
            "price": price,
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self.get_filling_mode(symbol)
        }

        result = self.send_market_order(request)

        connector.disconnect()

        if result is None:

            
            return {
                "success": False,
                "message": "Unable to execute order"
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            return {
                "success": False,
                "message": "Order execution failed.",
                "retcode": result.retcode,
                "comment": result.comment
            }

        return {
            "success": True,
            "message": "Market order executed successfully.",
            "data": {
                "ticket": result.order,
                "deal": result.deal,
                "price": result.price,
                "volume": result.volume,
                "retcode": result.retcode
            }
        }

    def close_position(self, ticket):

        status = connector.connect()

        if not status["success"]:
            return status

        positions = mt5.positions_get(ticket=ticket)

        if not positions:

            connector.disconnect()

            return {
                "success": False,
                "message": "Position not found."
            }

        position = positions[0]

        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Unable to fetch market price."
            }

        if position.type == mt5.POSITION_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": position.magic,
            "comment": "JD-Algo Close",
            "type_time": mt5.ORDER_TIME_GTC
        }

        result = self.send_market_order(request)

        connector.disconnect()

        if result is None:

            return {
                "success": False,
                "message": "Unable to close position."
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            return {
                "success": False,
                "message": "Close position failed.",
                "retcode": result.retcode,
                "comment": result.comment
            }

        return {
            "success": True,
            "message": "Position closed successfully.",
            "data": {
                "ticket": result.order,
                "deal": result.deal
            }
        }

    def modify_position(self, ticket, sl=None, tp=None):

        status = connector.connect()

        if not status["success"]:
            return status

        positions = mt5.positions_get(ticket=ticket)

        if not positions:

            connector.disconnect()

            return {
                "success": False,
                "message": "Position not found."
            }

        position = positions[0]

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": position.symbol,
            "sl": position.sl if sl is None else float(sl),
            "tp": position.tp if tp is None else float(tp)
        }

        result = mt5.order_send(request)

        connector.disconnect()

        if result is None:

            return {
                "success": False,
                "message": "Unable to modify position."
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            return {
                "success": False,
                "message": "Modify failed.",
                "retcode": result.retcode,
                "comment": result.comment
            }

        return {
            "success": True,
            "message": "Position modified successfully."
        }

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

        status = connector.connect()

        if not status["success"]:
            return status

        order_map = {
            "BUY_LIMIT": mt5.ORDER_TYPE_BUY_LIMIT,
            "SELL_LIMIT": mt5.ORDER_TYPE_SELL_LIMIT,
            "BUY_STOP": mt5.ORDER_TYPE_BUY_STOP,
            "SELL_STOP": mt5.ORDER_TYPE_SELL_STOP
        }

        if order_type not in order_map:

            connector.disconnect()

            return {
                "success": False,
                "message": "Invalid pending order type."
            }

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_map[order_type],
            "price": float(price),
            "sl": float(sl),
            "tp": float(tp),
            "deviation": 20,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC
        }

        result = self.send_market_order(request)

        connector.disconnect()

        if result is None:

            return {
                "success": False,
                "message": "Unable to place pending order."
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:

            return {
                "success": False,
                "message": "Pending order failed.",
                "retcode": result.retcode,
                "comment": result.comment
            }

        return {
            "success": True,
            "message": "Pending order placed successfully.",
            "data": {
                "ticket": result.order,
                "deal": result.deal
            }
        }





execution_service = MT5Execution()