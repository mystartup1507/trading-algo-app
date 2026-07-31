from connector import connector
from execution import execution_service

from .order_builder import order_builder
from .order_validator import order_validator
from .live_execution_guard import live_execution_guard


class ExecutionController:

    def execute(
        self,
        symbol,
        direction,
        lot_size,
        stop_loss,
        take_profit,
        dry_run=True,
        confirmation_token=None
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
                        "executed": False,
                        "validation": validation_result
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
            # Step 4 — LIVE EXECUTION GUARD
            # ---------------------------------
            #
            # Even if dry_run=False is passed,
            # execution cannot continue unless
            # the Live Execution Guard approves
            # the request.
            #
            # LIVE_TRADING_ENABLED is currently
            # False inside live_execution_guard.py
            # so live execution remains blocked.
            # ---------------------------------

            guard_result = (
                live_execution_guard.validate(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    confirmation_token=(
                        confirmation_token
                    )
                )
            )

            if not guard_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Live execution blocked by "
                        "execution safety guard."
                    ),
                    "data": {
                        "stage": (
                            "LIVE_EXECUTION_GUARD"
                        ),
                        "dry_run": False,
                        "executed": False,
                        "guard": (
                            guard_result["data"]
                        )
                    }
                }

            # ---------------------------------
            # Step 5 — LIVE EXECUTION
            # ---------------------------------
            #
            # This section can only be reached
            # when:
            #
            # 1. Order Builder succeeds
            # 2. Order Validator succeeds
            # 3. dry_run is False
            # 4. Live Execution Guard succeeds
            #
            # Existing execution.py is reused.
            # ---------------------------------

            execution_result = (
                execution_service.market_order(
                    symbol=symbol,
                    volume=float(lot_size),
                    order_type=(
                        str(direction).upper()
                    ),
                    sl=float(stop_loss),
                    tp=float(take_profit),
                    comment="JD-Algo",
                    magic=10001
                )
            )

            # ---------------------------------
            # Step 6 — Standard execution result
            # ---------------------------------

            execution_success = (
                execution_result.get(
                    "success",
                    False
                )
            )

            return {
                "success": execution_success,
                "message": (
                    execution_result.get(
                        "message",
                        "Execution completed."
                    )
                ),
                "data": {
                    "stage": "LIVE_EXECUTION",
                    "dry_run": False,
                    "executed": execution_success,
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