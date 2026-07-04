import MetaTrader5 as mt5


class MT5Connector:

    def connect(self):

        if not mt5.initialize():
            return {
                "success": False,
                "error": mt5.last_error()
            }

        terminal = mt5.terminal_info()

        if terminal is None:
            return {
                "success": False,
                "error": "Unable to read terminal information."
            }

        if not terminal.connected:
            return {
                "success": False,
                "error": "MT5 terminal is not connected."
            }

        return {
            "success": True,
            "terminal": terminal
        }

    def disconnect(self):
        mt5.shutdown()


connector = MT5Connector()
