import MetaTrader5 as mt5


class MT5Connector:

    def __init__(self):
        self.login = None
        self.password = None
        self.server = None

    def configure(self, login, password, server):

        self.login = login
        self.password = password
        self.server = server

        return {
            "success": True,
            "message": "MT5 connection configuration saved."
        }

    def clear_configuration(self):

        self.login = None
        self.password = None
        self.server = None

    def connect(self):

        # --------------------------------------------------
        # Credential-based connection
        # --------------------------------------------------

        if (
            self.login is not None
            and self.password is not None
            and self.server
        ):

            try:
                login = int(self.login)
            except (TypeError, ValueError):

                return {
                    "success": False,
                    "error": "MT5 Login ID must be numeric."
                }

            initialized = mt5.initialize(
                server=self.server,
                login=login,
                password=self.password
            )

        else:

            # --------------------------------------------------
            # Existing terminal connection behavior
            # --------------------------------------------------

            initialized = mt5.initialize()

        if not initialized:

            return {
                "success": False,
                "error": mt5.last_error()
            }

        terminal = mt5.terminal_info()

        if terminal is None:

            mt5.shutdown()

            return {
                "success": False,
                "error": "Unable to read terminal information."
            }

        if not terminal.connected:

            mt5.shutdown()

            return {
                "success": False,
                "error": "MT5 terminal is not connected."
            }

        account = mt5.account_info()

        if account is None:

            mt5.shutdown()

            return {
                "success": False,
                "error": "Unable to verify MT5 account login."
            }

        return {
            "success": True,
            "terminal": terminal,
            "account": account
        }

    def disconnect(self):

        mt5.shutdown()


connector = MT5Connector()
