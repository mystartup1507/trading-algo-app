import MetaTrader5 as mt5

from connector import connector
from execution import execution_service


class PositionManager:

    # --------------------------------------------------
    # Get one open position by ticket
    # --------------------------------------------------

    def get_position(self, ticket):

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            try:
                ticket = int(ticket)

            except (TypeError, ValueError):

                return {
                    "success": False,
                    "message": "Invalid position ticket."
                }

            positions = mt5.positions_get(
                ticket=ticket
            )

            if positions is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to retrieve position."
                    ),
                    "mt5_error": mt5.last_error()
                }

            if len(positions) == 0:

                return {
                    "success": False,
                    "message": (
                        f"Open position {ticket} "
                        "was not found."
                    )
                }

            position = positions[0]

            return {
                "success": True,
                "message": (
                    "Position retrieved successfully."
                ),
                "data": self._position_to_dict(
                    position
                )
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Position retrieval error: "
                    f"{str(error)}"
                )
            }

        finally:

            connector.disconnect()

    # --------------------------------------------------
    # Get all currently open positions
    # --------------------------------------------------

    def get_open_positions(self):

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            positions = mt5.positions_get()

            if positions is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to retrieve "
                        "open positions."
                    ),
                    "mt5_error": mt5.last_error()
                }

            data = [
                self._position_to_dict(position)
                for position in positions
            ]

            return {
                "success": True,
                "message": (
                    "Open positions retrieved "
                    "successfully."
                ),
                "data": {
                    "count": len(data),
                    "positions": data
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Open-position retrieval error: "
                    f"{str(error)}"
                )
            }

        finally:

            connector.disconnect()

    # --------------------------------------------------
    # Modify position SL / TP
    #
    # Reuses existing execution.py functionality.
    # --------------------------------------------------

    def modify_position(
        self,
        ticket,
        stop_loss=None,
        take_profit=None
    ):

        position_result = self.get_position(
            ticket
        )

        if not position_result["success"]:
            return position_result

        position = position_result["data"]

        current_sl = float(
            position["sl"]
        )

        current_tp = float(
            position["tp"]
        )

        new_sl = (
            float(stop_loss)
            if stop_loss is not None
            else current_sl
        )

        new_tp = (
            float(take_profit)
            if take_profit is not None
            else current_tp
        )

        try:

            result = execution_service.modify_position(
                int(ticket),
                sl=new_sl,
                tp=new_tp
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Position modification error: "
                    f"{str(error)}"
                )
            }

        if not result["success"]:
            return result

        # ----------------------------------------------
        # Verify MT5 actually contains the new values
        # ----------------------------------------------

        verification = self.get_position(
            ticket
        )

        if not verification["success"]:

            return {
                "success": False,
                "message": (
                    "Position modification was sent, "
                    "but verification failed."
                ),
                "data": {
                    "modification": result,
                    "verification": verification
                }
            }

        verified_position = verification["data"]

        return {
            "success": True,
            "message": (
                "Position modified and verified "
                "successfully."
            ),
            "data": {
                "ticket": int(ticket),
                "symbol": verified_position["symbol"],
                "stop_loss": verified_position["sl"],
                "take_profit": verified_position["tp"],
                "position": verified_position
            }
        }

    # --------------------------------------------------
    # Close one open position
    #
    # Reuses existing execution.py functionality.
    # --------------------------------------------------

    def close_position(self, ticket):

        position_result = self.get_position(
            ticket
        )

        if not position_result["success"]:
            return position_result

        position_before = position_result["data"]

        try:

            result = execution_service.close_position(
                int(ticket)
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Position close error: "
                    f"{str(error)}"
                )
            }

        if not result["success"]:
            return result

        # ----------------------------------------------
        # Verify the position disappeared from MT5
        # ----------------------------------------------

        status = connector.connect()

        if not status["success"]:

            return {
                "success": False,
                "message": (
                    "Position close was sent, "
                    "but verification connection failed."
                ),
                "data": {
                    "close_result": result
                }
            }

        try:

            remaining = mt5.positions_get(
                ticket=int(ticket)
            )

            if remaining is None:

                return {
                    "success": False,
                    "message": (
                        "Position close was sent, "
                        "but verification failed."
                    ),
                    "mt5_error": mt5.last_error(),
                    "data": {
                        "close_result": result
                    }
                }

            closed = len(remaining) == 0

        finally:

            connector.disconnect()

        if not closed:

            return {
                "success": False,
                "message": (
                    "Close request completed but "
                    "the position is still open."
                ),
                "data": {
                    "ticket": int(ticket),
                    "closed": False,
                    "close_result": result
                }
            }

        return {
            "success": True,
            "message": (
                "Position closed and verified "
                "successfully."
            ),
            "data": {
                "ticket": int(ticket),
                "symbol": position_before["symbol"],
                "volume": position_before["volume"],
                "closed": True,
                "close_result": result
            }
        }

           # --------------------------------------------------
    # Controlled close of JD-Algo demo test position
    # --------------------------------------------------

    def controlled_close(
        self,
        ticket,
        confirmation_token=None
    ):

        REQUIRED_TOKEN = "CONFIRM_CLOSE_POSITION"
        CONTROLLED_SYMBOL = "EURUSD#"
        CONTROLLED_VOLUME = 0.01
        JD_ALGO_MAGIC = 10001

        # ----------------------------------------------
        # Confirmation token
        # ----------------------------------------------

        if confirmation_token != REQUIRED_TOKEN:

            return {
                "success": False,
                "message": (
                    "Position close blocked: "
                    "invalid confirmation token."
                )
            }

        # ----------------------------------------------
        # Retrieve position
        # ----------------------------------------------

        position_result = self.get_position(ticket)

        if not position_result["success"]:
            return position_result

        position = position_result["data"]

        checks = {
            "symbol": (
                position["symbol"]
                == CONTROLLED_SYMBOL
            ),
            "volume": (
                abs(
                    float(position["volume"])
                    - CONTROLLED_VOLUME
                ) < 0.0000001
            ),
            "magic": (
                int(position["magic"])
                == JD_ALGO_MAGIC
            ),
            "comment": (
                position["comment"]
                == "JD-Algo"
            )
        }

        # ----------------------------------------------
        # Verify connected account is demo
        # ----------------------------------------------

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            account = mt5.account_info()

            if account is None:

                checks["account_available"] = False
                checks["demo_account"] = False

            else:

                checks["account_available"] = True

                checks["demo_account"] = (
                    "demo"
                    in str(account.name).lower()
                )

                checks["trade_allowed"] = (
                    account.trade_allowed is True
                )

                checks["trade_expert"] = (
                    account.trade_expert is True
                )

        finally:

            connector.disconnect()

        failed_checks = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        if failed_checks:

            return {
                "success": False,
                "message": (
                    "Position close blocked by "
                    "safety validation."
                ),
                "data": {
                    "ticket": int(ticket),
                    "checks": checks,
                    "failed_checks": failed_checks
                }
            }

        # ----------------------------------------------
        # Existing close + verification implementation
        # ----------------------------------------------

        result = self.close_position(ticket)

        if not result["success"]:
            return result

        return {
            "success": True,
            "message": (
                "Controlled demo position closed "
                "and verified successfully."
            ),
            "data": {
                "ticket": int(ticket),
                "checks": checks,
                "closed": True,
                "result": result
            }
        }

    # --------------------------------------------------
    # Convert MT5 position object to JSON-safe dictionary
    # --------------------------------------------------

    def _position_to_dict(
        self,
        position
    ):

        position_type = int(
            position.type
        )

        if position_type == mt5.POSITION_TYPE_BUY:
            direction = "BUY"

        elif position_type == mt5.POSITION_TYPE_SELL:
            direction = "SELL"

        else:
            direction = "UNKNOWN"

        return {
            "ticket": int(position.ticket),
            "symbol": position.symbol,
            "direction": direction,
            "volume": float(position.volume),
            "price_open": float(
                position.price_open
            ),
            "price_current": float(
                position.price_current
            ),
            "sl": float(position.sl),
            "tp": float(position.tp),
            "profit": float(position.profit),
            "swap": float(position.swap),
            "magic": int(position.magic),
            "comment": position.comment,
            "time": int(position.time),
            "time_msc": int(
                position.time_msc
            )
        }


position_manager = PositionManager()