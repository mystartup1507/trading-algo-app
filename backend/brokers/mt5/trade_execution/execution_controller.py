from connector import connector
from execution import execution_service

from .order_builder import order_builder
from .order_validator import order_validator


class ExecutionController:

    def execute(
        self,
        symbol,
        direction,
        lot_size,
        stop_loss,
        take_profit,
        dry_run=True
    ):

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            # ---------------------------------
            # Step 1 — Build MT5 order request
            # ---------------------------------

            build_result = order_builder.build(
                symbol,
                direction,
                lot_size,
                stop_loss,
                take_profit
            )

            if not build_result["success"]:
                return build_result

            request_data = (
                build_result["data"]["request"]
            )

            # ---------------------------------
            # Step 2 — Pre-execution validation
            # ---------------------------------

            validation_result = (
                order_validator.validate(
                    request_data
                )
            )

            if not validation_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Execution blocked by "
                        "pre-execution validation."
                    ),
                    "data": {
                        "stage": "VALIDATION",
                        "dry_run": bool(dry_run),
                        "validation": (
                            validation_result
                        )
                    }
                }

            # ---------------------------------
            # Step 3 — DRY RUN safety barrier
            # ---------------------------------

            if dry_run:

                return {
                    "success": True,
                    "message": (
                        "Dry run completed successfully. "
                        "No order was sent to MT5."
                    ),
                    "data": {
                        "stage": "DRY_RUN",
                        "dry_run": True,
                        "symbol": symbol,
                        "direction": (
                            str(direction).upper()
                        ),
                        "lot_size": float(lot_size),
                        "stop_loss": float(stop_loss),
                        "take_profit": float(take_profit),
                        "order": request_data,
                        "validation": (
                            validation_result["data"]
                        ),
                        "executed": False
                    }
                }

            # ---------------------------------
            # Step 4 — LIVE EXECUTION
            # ---------------------------------
            #
            # This section is unreachable while
            # dry_run=True.
            #
            # We deliberately use the existing,
            # previously working execution.py
            # service rather than creating another
            # MT5 order sender.
            # ---------------------------------

            execution_result = (
                execution_service.market_order(
                    symbol=symbol,
                    volume=float(lot_size),
                    order_type=str(direction).upper(),
                    sl=float(stop_loss),
                    tp=float(take_profit),
                    comment="JD-Algo",
                    magic=10001
                )
            )

            return {
                "success": (
                    execution_result.get(
                        "success",
                        False
                    )
                ),
                "message": (
                    execution_result.get(
                        "message",
                        "Execution completed."
                    )
                ),
                "data": {
                    "stage": "LIVE_EXECUTION",
                    "dry_run": False,
                    "executed": (
                        execution_result.get(
                            "success",
                            False
                        )
                    ),
                    "execution": execution_result
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Execution Controller error: "
                    f"{str(error)}"
                ),
                "data": {
                    "stage": "ERROR",
                    "dry_run": bool(dry_run),
                    "executed": False
                }
            }

        finally:

            connector.disconnect()


execution_controller = ExecutionController()