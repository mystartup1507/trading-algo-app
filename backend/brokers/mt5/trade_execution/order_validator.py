import MetaTrader5 as mt5


class OrderValidator:

    def validate(self, request):

        try:
            if not isinstance(request, dict):
                return {
                    "success": False,
                    "message": "Invalid order request."
                }

            # ---------------------------------
            # Required fields
            # ---------------------------------

            required_fields = [
                "symbol",
                "volume",
                "type",
                "price",
                "sl",
                "tp"
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in request
            ]

            if missing_fields:
                return {
                    "success": False,
                    "message": "Order request is missing required fields.",
                    "data": {
                        "missing_fields": missing_fields
                    }
                }

            symbol = str(request["symbol"]).strip()
            volume = float(request["volume"])
            price = float(request["price"])
            stop_loss = float(request["sl"])
            take_profit = float(request["tp"])
            order_type = request["type"]

            # ---------------------------------
            # Symbol
            # ---------------------------------

            info = mt5.symbol_info(symbol)

            if info is None:
                return {
                    "success": False,
                    "message": f"Symbol '{symbol}' not found."
                }

            if not info.visible:
                if not mt5.symbol_select(symbol, True):
                    return {
                        "success": False,
                        "message": f"Unable to select symbol '{symbol}'."
                    }

                info = mt5.symbol_info(symbol)

                if info is None:
                    return {
                        "success": False,
                        "message": f"Unable to reload symbol '{symbol}'."
                    }

            # ---------------------------------
            # Live tick
            # ---------------------------------

            tick = mt5.symbol_info_tick(symbol)

            if tick is None:
                return {
                    "success": False,
                    "message": "Unable to retrieve live market price."
                }

            # ---------------------------------
            # Volume
            # ---------------------------------

            volume_valid = (
                info.volume_min
                <= volume
                <= info.volume_max
            )

            step = float(info.volume_step)

            if step <= 0:
                volume_step_valid = False
            else:
                steps = round(volume / step)
                normalized_volume = steps * step

                volume_step_valid = (
                    abs(volume - normalized_volume) < 1e-8
                )

            # ---------------------------------
            # Direction / price
            # ---------------------------------

            if order_type == mt5.ORDER_TYPE_BUY:

                direction = "BUY"
                live_price = float(tick.ask)

                stop_loss_valid = (
                    stop_loss == 0
                    or stop_loss < live_price
                )

                take_profit_valid = (
                    take_profit == 0
                    or take_profit > live_price
                )

            elif order_type == mt5.ORDER_TYPE_SELL:

                direction = "SELL"
                live_price = float(tick.bid)

                stop_loss_valid = (
                    stop_loss == 0
                    or stop_loss > live_price
                )

                take_profit_valid = (
                    take_profit == 0
                    or take_profit < live_price
                )

            else:
                return {
                    "success": False,
                    "message": "Unsupported market order type."
                }

            # ---------------------------------
            # Broker minimum stop distance
            # ---------------------------------

            point = float(info.point)
            stops_level = int(info.trade_stops_level)

            minimum_stop_distance = (
                stops_level * point
            )

            if stop_loss == 0:
                stop_distance_valid = True
            else:
                stop_distance_valid = (
                    abs(live_price - stop_loss)
                    >= minimum_stop_distance
                )

            if take_profit == 0:
                target_distance_valid = True
            else:
                target_distance_valid = (
                    abs(take_profit - live_price)
                    >= minimum_stop_distance
                )

            # ---------------------------------
            # Spread
            # ---------------------------------

            spread = float(tick.ask - tick.bid)

            if point > 0:
                spread_points = spread / point
            else:
                spread_points = 0

            # ---------------------------------
            # Local checks
            # ---------------------------------

            checks = {
                "volume": volume_valid,
                "volume_step": volume_step_valid,
                "stop_loss": stop_loss_valid,
                "take_profit": take_profit_valid,
                "stop_distance": stop_distance_valid,
                "target_distance": target_distance_valid
            }

            local_valid = all(checks.values())

            if not local_valid:

                failed_checks = [
                    name
                    for name, passed in checks.items()
                    if not passed
                ]

                return {
                    "success": False,
                    "message": "Pre-execution validation failed.",
                    "data": {
                        "valid": False,
                        "direction": direction,
                        "live_price": live_price,
                        "spread_points": round(
                            spread_points,
                            1
                        ),
                        "minimum_stop_distance": (
                            minimum_stop_distance
                        ),
                        "checks": checks,
                        "failed_checks": failed_checks
                    }
                }

            # ---------------------------------
            # MT5 native order_check
            # ---------------------------------

            check_request = dict(request)

            # Validate against the latest market price.
            check_request["price"] = live_price

            order_check = mt5.order_check(
                check_request
            )

            if order_check is None:

                return {
                    "success": False,
                    "message": "MT5 order_check returned no result.",
                    "data": {
                        "last_error": mt5.last_error()
                    }
                }

            mt5_valid = (
                order_check.retcode == 0
            )

            if not mt5_valid:

                return {
                    "success": False,
                    "message": "MT5 rejected the order during pre-check.",
                    "data": {
                        "valid": False,
                        "retcode": order_check.retcode,
                        "comment": order_check.comment,
                        "direction": direction,
                        "live_price": live_price,
                        "spread_points": round(
                            spread_points,
                            1
                        ),
                        "checks": checks
                    }
                }

            return {
                "success": True,
                "message": "Pre-execution validation passed.",
                "data": {
                    "valid": True,
                    "symbol": symbol,
                    "direction": direction,
                    "volume": volume,
                    "live_price": live_price,
                    "spread_points": round(
                        spread_points,
                        1
                    ),
                    "minimum_stop_distance": (
                        minimum_stop_distance
                    ),
                    "checks": checks,
                    "mt5_order_check": {
                        "retcode": order_check.retcode,
                        "comment": order_check.comment
                    },
                    "failed_checks": []
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    f"Order Validator error: {str(error)}"
                )
            }


order_validator = OrderValidator()