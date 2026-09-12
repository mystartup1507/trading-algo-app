import MetaTrader5 as mt5

from connector import connector


class MaxOpenPositionsGuard:

    MAX_OPEN_POSITIONS = 3

    def validate(self):

        status = connector.connect()

        if not status["success"]:

            return status

        try:

            positions = mt5.positions_get()

            if positions is None:

                positions = []

            count = len(positions)

            if count >= self.MAX_OPEN_POSITIONS:

                return {
                    "success": False,
                    "message": "Maximum open positions reached.",
                    "data": {
                        "allowed": False,
                        "open_positions": count,
                        "maximum_positions": self.MAX_OPEN_POSITIONS
                    }
                }

            return {
                "success": True,
                "message": "Maximum open position validation passed.",
                "data": {
                    "allowed": True,
                    "open_positions": count,
                    "maximum_positions": self.MAX_OPEN_POSITIONS,
                    "remaining_positions": (
                        self.MAX_OPEN_POSITIONS - count
                    )
                }
            }

        finally:

            connector.disconnect()


max_open_positions_guard = MaxOpenPositionsGuard()