import MetaTrader5 as mt5

from connector import connector


class LiveExecutionGuard:

    # --------------------------------------------------
    # MASTER LIVE-TRADING SWITCH
    # --------------------------------------------------
    # KEEP FALSE until all safety tests have passed.
    # --------------------------------------------------

    LIVE_TRADING_ENABLED = False

    # Explicit confirmation required.
    CONFIRMATION_TOKEN = "CONFIRM_LIVE_TRADE"

    # --------------------------------------------------
    # CONTROLLED TEST SETTINGS
    # --------------------------------------------------

    DEMO_ONLY = True
    TEST_LOT_SIZE = 0.01
    CONTROLLED_TEST_SYMBOL = "EURUSD#"

    def validate(
        self,
        symbol,
        direction,
        lot_size,
        confirmation_token=None
    ):

        checks = {}

        # --------------------------------------------------
        # 1. Master live-trading switch
        # --------------------------------------------------

        checks["live_trading_enabled"] = (
            self.LIVE_TRADING_ENABLED is True
        )

        # --------------------------------------------------
        # 2. Confirmation token
        # --------------------------------------------------

        checks["confirmation_token"] = (
            confirmation_token
            == self.CONFIRMATION_TOKEN
        )

        # --------------------------------------------------
        # 3. Symbol
        # --------------------------------------------------

        symbol = (
            str(symbol).strip()
            if symbol is not None
            else ""
        )

        checks["symbol"] = (
            symbol != ""
        )

        # --------------------------------------------------
# Controlled-test symbol restriction
# --------------------------------------------------

        checks["controlled_test_symbol"] = (
            symbol == self.CONTROLLED_TEST_SYMBOL
        )

        # --------------------------------------------------
        # 4. Direction
        # --------------------------------------------------

        direction = (
            str(direction).upper().strip()
            if direction is not None
            else ""
        )

        checks["direction"] = (
            direction in ["BUY", "SELL"]
        )

        # --------------------------------------------------
        # 5. Lot size
        # --------------------------------------------------

        try:

            volume = float(lot_size)

            checks["lot_size"] = (
                volume > 0
            )

        except (TypeError, ValueError):

            volume = 0.0
            checks["lot_size"] = False

        # --------------------------------------------------
        # 6. Controlled-test volume restriction
        # --------------------------------------------------

        checks["controlled_test_volume"] = (
            abs(volume - self.TEST_LOT_SIZE)
            < 0.0000001
        )

        # --------------------------------------------------
        # 7. Connect to MT5
        # --------------------------------------------------

        connection_status = connector.connect()

        if not connection_status["success"]:

            checks["mt5_connection"] = False
            checks["account_available"] = False
            checks["demo_account"] = False
            checks["trade_allowed"] = False
            checks["trade_expert"] = False

            return self._blocked_result(
                checks=checks,
                account=None
            )

        checks["mt5_connection"] = True

        try:

            # --------------------------------------------------
            # 8. Get connected MT5 account
            # --------------------------------------------------

            account_info = mt5.account_info()

            if account_info is None:

                checks["account_available"] = False
                checks["demo_account"] = False
                checks["trade_allowed"] = False
                checks["trade_expert"] = False

                return self._blocked_result(
                    checks=checks,
                    account=None
                )

            checks["account_available"] = True

            account_name = str(
                account_info.name
            ).strip()

            # --------------------------------------------------
            # 9. Demo-account restriction
            # --------------------------------------------------

            if self.DEMO_ONLY:

                checks["demo_account"] = (
                    "demo" in account_name.lower()
                )

            else:

                checks["demo_account"] = True

            # --------------------------------------------------
            # 10. MT5 trading permissions
            # --------------------------------------------------

            checks["trade_allowed"] = (
                account_info.trade_allowed is True
            )

            checks["trade_expert"] = (
                account_info.trade_expert is True
            )

            # --------------------------------------------------
            # 11. Final decision
            # --------------------------------------------------

            account_data = {
                "name": account_name,
                "server": account_info.server,
                "company": account_info.company,
                "currency": account_info.currency,
                "balance": account_info.balance,
                "equity": account_info.equity,
                "trade_allowed": (
                    account_info.trade_allowed
                ),
                "trade_expert": (
                    account_info.trade_expert
                )
            }

            valid = all(checks.values())

            if not valid:

                return self._blocked_result(
                    checks=checks,
                    account=account_data
                )

            return {
                "success": True,
                "message": (
                    "Live execution safety checks passed."
                ),
                "data": {
                    "allowed": True,
                    "checks": checks,
                    "failed_checks": [],
                    "account": account_data,
                    "controlled_test_volume": (
                        self.TEST_LOT_SIZE
                    )
                }
            }

        finally:

            connector.disconnect()

    def _blocked_result(
        self,
        checks,
        account=None
    ):

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        return {
            "success": False,
            "message": (
                "Live execution blocked by "
                "execution safety guard."
            ),
            "data": {
                "allowed": False,
                "checks": checks,
                "failed_checks": failed_checks,
                "account": account,
                "controlled_test_volume": (
                    self.TEST_LOT_SIZE
                )
            }
        }


live_execution_guard = LiveExecutionGuard()