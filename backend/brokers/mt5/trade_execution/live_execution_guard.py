import MetaTrader5 as mt5

from connector import connector


class LiveExecutionGuard:

    # ==========================================================
    # MASTER LIVE-TRADING SWITCH
    # ==========================================================
    #
    # IMPORTANT:
    # Keep this FALSE while normal development/testing continues.
    #
    # We will enable it only for the controlled demo live-order
    # test after the remaining safety checks are verified.
    #
    # ==========================================================

    LIVE_TRADING_ENABLED = True

    # ==========================================================
    # EXPLICIT LIVE CONFIRMATION
    # ==========================================================

    CONFIRMATION_TOKEN = "CONFIRM_LIVE_TRADE"

    # ==========================================================
    # CONTROLLED TEST SETTINGS
    # ==========================================================

    DEMO_ONLY = True

    TEST_LOT_SIZE = 0.01

    CONTROLLED_TEST_SYMBOL = "EURUSD#"

    LOT_TOLERANCE = 0.0000001

    # ==========================================================
    # VALIDATE
    # ==========================================================

    def validate(
        self,
        symbol,
        direction,
        lot_size,
        confirmation_token=None
    ):

        checks = {}

        # ------------------------------------------------------
        # Normalize symbol
        # ------------------------------------------------------

        symbol = (
            str(symbol).strip()
            if symbol is not None
            else ""
        )

        # ------------------------------------------------------
        # Normalize direction
        # ------------------------------------------------------

        direction = (
            str(direction).upper().strip()
            if direction is not None
            else ""
        )

        # ------------------------------------------------------
        # Normalize volume
        # ------------------------------------------------------

        try:

            volume = float(lot_size)

        except (TypeError, ValueError):

            volume = 0.0

        # ======================================================
        # 1. MASTER LIVE SWITCH
        # ======================================================

        checks["live_trading_enabled"] = (
            self.LIVE_TRADING_ENABLED is True
        )

        # ======================================================
        # 2. EXPLICIT CONFIRMATION TOKEN
        # ======================================================

        checks["confirmation_token"] = (
            confirmation_token
            == self.CONFIRMATION_TOKEN
        )

        # ======================================================
        # 3. SYMBOL VALIDATION
        # ======================================================

        checks["symbol"] = (
            symbol != ""
        )

        # ======================================================
        # 4. CONTROLLED TEST SYMBOL
        # ======================================================

        checks["controlled_test_symbol"] = (
            symbol == self.CONTROLLED_TEST_SYMBOL
        )

        # ======================================================
        # 5. DIRECTION
        # ======================================================

        checks["direction"] = (
            direction in ["BUY", "SELL"]
        )

        # ======================================================
        # 6. LOT SIZE
        # ======================================================

        checks["lot_size"] = (
            volume > 0
        )

        # ======================================================
        # 7. CONTROLLED TEST LOT SIZE
        # ======================================================

        checks["controlled_test_volume"] = (
            abs(
                volume
                - self.TEST_LOT_SIZE
            )
            < self.LOT_TOLERANCE
        )

        # ======================================================
        # 8. MT5 CONNECTION
        # ======================================================

        connection_status = connector.connect()

        if not connection_status.get(
            "success",
            False
        ):

            checks["mt5_connection"] = False
            checks["account_available"] = False
            checks["demo_account"] = False
            checks["trade_allowed"] = False
            checks["trade_expert"] = False
            checks["symbol_available"] = False
            checks["symbol_trade_enabled"] = False

            return self._blocked_result(
                checks=checks,
                account=None,
                symbol_data=None
            )

        checks["mt5_connection"] = True

        try:

            # ==================================================
            # 9. ACCOUNT INFORMATION
            # ==================================================

            account_info = mt5.account_info()

            if account_info is None:

                checks["account_available"] = False
                checks["demo_account"] = False
                checks["trade_allowed"] = False
                checks["trade_expert"] = False
                checks["symbol_available"] = False
                checks["symbol_trade_enabled"] = False

                return self._blocked_result(
                    checks=checks,
                    account=None,
                    symbol_data=None
                )

            checks["account_available"] = True

            account_name = str(
                account_info.name
            ).strip()

            # ==================================================
            # 10. DEMO ACCOUNT RESTRICTION
            # ==================================================

            if self.DEMO_ONLY:

                checks["demo_account"] = (
                    "demo"
                    in account_name.lower()
                    or "demo"
                    in str(
                        account_info.server
                    ).lower()
                )

            else:

                checks["demo_account"] = True

            # ==================================================
            # 11. ACCOUNT TRADING PERMISSIONS
            # ==================================================

            checks["trade_allowed"] = bool(
                account_info.trade_allowed
            )

            checks["trade_expert"] = bool(
                account_info.trade_expert
            )

            # ==================================================
            # 12. SYMBOL INFORMATION
            # ==================================================

            symbol_info = mt5.symbol_info(
                symbol
            )

            if symbol_info is None:

                checks["symbol_available"] = False
                checks["symbol_trade_enabled"] = False

                account_data = (
                    self._build_account_data(
                        account_info
                    )
                )

                return self._blocked_result(
                    checks=checks,
                    account=account_data,
                    symbol_data=None
                )

            checks["symbol_available"] = True

            # --------------------------------------------------
            # MT5 trade_mode:
            #
            # SYMBOL_TRADE_MODE_DISABLED = 0
            #
            # Anything other than DISABLED means that some form
            # of trading is available for the symbol.
            # --------------------------------------------------

            checks["symbol_trade_enabled"] = (
                symbol_info.trade_mode
                != mt5.SYMBOL_TRADE_MODE_DISABLED
            )

            # ==================================================
            # 13. BUILD DIAGNOSTIC DATA
            # ==================================================

            account_data = (
                self._build_account_data(
                    account_info
                )
            )

            symbol_data = {
                "symbol": symbol,
                "description": (
                    symbol_info.description
                ),
                "trade_mode": (
                    symbol_info.trade_mode
                ),
                "volume_min": (
                    symbol_info.volume_min
                ),
                "volume_max": (
                    symbol_info.volume_max
                ),
                "volume_step": (
                    symbol_info.volume_step
                ),
                "trade_contract_size": (
                    symbol_info.trade_contract_size
                )
            }

            # ==================================================
            # 14. BROKER VOLUME RANGE
            # ==================================================

            checks["broker_min_volume"] = (
                volume
                >= symbol_info.volume_min
            )

            checks["broker_max_volume"] = (
                volume
                <= symbol_info.volume_max
            )

            # ==================================================
            # 15. BROKER VOLUME STEP
            # ==================================================

            step = float(
                symbol_info.volume_step
            )

            minimum = float(
                symbol_info.volume_min
            )

            if step > 0:

                steps = (
                    (volume - minimum)
                    / step
                )

                checks["broker_volume_step"] = (
                    abs(
                        steps
                        - round(steps)
                    )
                    < 0.000001
                )

            else:

                checks["broker_volume_step"] = False

            # ==================================================
            # FINAL DECISION
            # ==================================================

            valid = all(
                checks.values()
            )

            failed_checks = [
                name
                for name, passed
                in checks.items()
                if not passed
            ]

            if not valid:

                return self._blocked_result(
                    checks=checks,
                    account=account_data,
                    symbol_data=symbol_data
                )

            return {
                "success": True,
                "message": (
                    "Live execution safety "
                    "checks passed."
                ),
                "data": {
                    "allowed": True,
                    "mode": (
                        "CONTROLLED_DEMO_LIVE"
                    ),
                    "symbol": symbol,
                    "direction": direction,
                    "lot_size": volume,
                    "checks": checks,
                    "failed_checks": (
                        failed_checks
                    ),
                    "account": (
                        account_data
                    ),
                    "symbol_info": (
                        symbol_data
                    ),
                    "safety_limits": {
                        "demo_only": (
                            self.DEMO_ONLY
                        ),
                        "controlled_symbol": (
                            self.CONTROLLED_TEST_SYMBOL
                        ),
                        "controlled_lot_size": (
                            self.TEST_LOT_SIZE
                        ),
                        "live_trading_enabled": (
                            self.LIVE_TRADING_ENABLED
                        )
                    }
                }
            }

        finally:

            connector.disconnect()

    # ==========================================================
    # ACCOUNT DATA
    # ==========================================================

    def _build_account_data(
        self,
        account_info
    ):

        return {
            "login": (
                account_info.login
            ),
            "name": (
                str(
                    account_info.name
                ).strip()
            ),
            "server": (
                account_info.server
            ),
            "company": (
                account_info.company
            ),
            "currency": (
                account_info.currency
            ),
            "balance": (
                account_info.balance
            ),
            "equity": (
                account_info.equity
            ),
            "margin": (
                account_info.margin
            ),
            "margin_free": (
                account_info.margin_free
            ),
            "leverage": (
                account_info.leverage
            ),
            "trade_allowed": (
                bool(
                    account_info.trade_allowed
                )
            ),
            "trade_expert": (
                bool(
                    account_info.trade_expert
                )
            )
        }

    # ==========================================================
    # BLOCKED RESULT
    # ==========================================================

    def _blocked_result(
        self,
        checks,
        account=None,
        symbol_data=None
    ):

        failed_checks = [
            name
            for name, passed
            in checks.items()
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
                "mode": (
                    "CONTROLLED_DEMO_LIVE"
                ),
                "checks": checks,
                "failed_checks": (
                    failed_checks
                ),
                "account": account,
                "symbol_info": (
                    symbol_data
                ),
                "safety_limits": {
                    "demo_only": (
                        self.DEMO_ONLY
                    ),
                    "controlled_symbol": (
                        self.CONTROLLED_TEST_SYMBOL
                    ),
                    "controlled_lot_size": (
                        self.TEST_LOT_SIZE
                    ),
                    "live_trading_enabled": (
                        self.LIVE_TRADING_ENABLED
                    )
                }
            }
        }


live_execution_guard = LiveExecutionGuard()