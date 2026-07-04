import MetaTrader5 as mt5
from connector import connector


class MT5Account:

    def get_account_info(self):

        status = connector.connect()

        if not status["success"]:
            return status

        account = mt5.account_info()

        if account is None:
            connector.disconnect()

            return {
                "success": False,
                "error": "Unable to retrieve account information."
            }

        data = account._asdict()

        connector.disconnect()

        return {
            "success": True,
            "data": data
        }


account_service = MT5Account()
