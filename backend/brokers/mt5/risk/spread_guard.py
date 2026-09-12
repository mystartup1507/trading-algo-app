import MetaTrader5 as mt5

from connector import connector


class SpreadGuard:

    # =====================================================
    # Maximum allowed spread (points)
    # =====================================================

    MAX_SPREAD_POINTS = 20

    # =====================================================

    def validate(self, symbol):

        status = connector.connect()

        if not status["success"]:

            return {
                "success": False,
                "message": "Unable to connect to MT5."
            }

        try:

            info = mt5.symbol_info(symbol)

            tick = mt5.symbol_info_tick(symbol)

            if info is None or tick is None:

                return {
                    "success": False,
                    "message": "Unable to read symbol information."
                }

            spread_points = (
                (tick.ask - tick.bid)
                / info.point
            )

            allowed = (
                spread_points
                <= self.MAX_SPREAD_POINTS
            )

            return {
                "success": allowed,
                "message": (
                    "Spread validation passed."
                    if allowed
                    else "Spread too high."
                ),
                "data": {
                    "allowed": allowed,
                    "symbol": symbol,
                    "bid": tick.bid,
                    "ask": tick.ask,
                    "point": info.point,
                    "spread_points": round(
                        spread_points,
                        2
                    ),
                    "maximum_allowed_points": (
                        self.MAX_SPREAD_POINTS
                    )
                }
            }

        finally:

            connector.disconnect()


spread_guard = SpreadGuard()