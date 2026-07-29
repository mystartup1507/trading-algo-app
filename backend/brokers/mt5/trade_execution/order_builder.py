import MetaTrader5 as mt5


class OrderBuilder:

    def build(
        self,
        symbol,
        direction,
        lot_size,
        stop_loss,
        take_profit,
        deviation=20,
        magic=10001,
        comment="JD-Algo"
    ):

        try:

            # -----------------------------
            # Basic validation
            # -----------------------------

            direction = str(direction).upper().strip()
            symbol = str(symbol).strip()

            if direction not in ["BUY", "SELL"]:
                return {
                    "success": False,
                    "message": "Invalid trade direction."
                }

            if lot_size <= 0:
                return {
                    "success": False,
                    "message": "Lot size must be greater than zero."
                }

            # -----------------------------
            # Get symbol information
            # -----------------------------

            symbol_info = mt5.symbol_info(symbol)

            if symbol_info is None:
                return {
                    "success": False,
                    "message": f"Symbol not found: {symbol}"
                }

            # Make symbol visible if needed
            if not symbol_info.visible:

                if not mt5.symbol_select(symbol, True):

                    return {
                        "success": False,
                        "message": f"Unable to select symbol: {symbol}"
                    }

            # -----------------------------
            # Get current market price
            # -----------------------------

            tick = mt5.symbol_info_tick(symbol)

            if tick is None:
                return {
                    "success": False,
                    "message": "Unable to retrieve current market price."
                }

            # -----------------------------
            # BUY order
            # -----------------------------

            if direction == "BUY":

                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask

            # -----------------------------
            # SELL order
            # -----------------------------

            else:

                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid

            # -----------------------------
            # Build MT5 request
            # -----------------------------

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(lot_size),
                "type": order_type,
                "price": float(price),
                "sl": float(stop_loss),
                "tp": float(take_profit),
                "deviation": int(deviation),
                "magic": int(magic),
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC
            }

            return {
                "success": True,
                "message": "Order request built successfully.",
                "data": {
                    "symbol": symbol,
                    "direction": direction,
                    "lot_size": float(lot_size),
                    "entry_price": float(price),
                    "stop_loss": float(stop_loss),
                    "take_profit": float(take_profit),
                    "request": request
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": f"Order Builder error: {str(error)}"
            }


order_builder = OrderBuilder()