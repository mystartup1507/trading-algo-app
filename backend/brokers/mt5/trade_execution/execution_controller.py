from connector import connector
from execution import execution_service

from .order_builder import order_builder
from .order_validator import order_validator
from .live_execution_guard import live_execution_guard
from .trade_lifecycle_manager import trade_lifecycle_manager


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

        execution_lock_acquired = False

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
            #
            # Dry-run behavior remains unchanged.
            # Lifecycle state is not modified by
            # a simulation.
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
            # Step 5 — Reliability check
            # ---------------------------------
            #
            # Prevent another JD-Algo position
            # from being opened on the same
            # symbol.
            # ---------------------------------

            reliability_result = (
                trade_lifecycle_manager
                .pre_execution_check(symbol)
            )

            if not reliability_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Execution blocked by "
                        "trade lifecycle protection."
                    ),
                    "data": {
                        "stage": "RELIABILITY_CHECK",
                        "dry_run": False,
                        "executed": False,
                        "reliability": (
                            reliability_result["data"]
                        )
                    }
                }

            # ---------------------------------
            # Step 6 — Acquire execution lock
            # ---------------------------------

            lock_result = (
                trade_lifecycle_manager
                .acquire_execution_lock()
            )

            if not lock_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Execution blocked because "
                        "another trade is already "
                        "being processed."
                    ),
                    "data": {
                        "stage": "EXECUTION_LOCK",
                        "dry_run": False,
                        "executed": False,
                        "lock": lock_result
                    }
                }

            execution_lock_acquired = True

            # ---------------------------------
            # Step 7 — Re-check after lock
            # ---------------------------------
            #
            # This second check is important.
            # Another request could have passed
            # the first duplicate check before
            # this request acquired the lock.
            # ---------------------------------

            reliability_result = (
                trade_lifecycle_manager
                .pre_execution_check(symbol)
            )

            if not reliability_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Execution blocked by "
                        "post-lock reliability check."
                    ),
                    "data": {
                        "stage": (
                            "POST_LOCK_RELIABILITY_CHECK"
                        ),
                        "dry_run": False,
                        "executed": False,
                        "reliability": (
                            reliability_result["data"]
                        )
                    }
                }

            # ---------------------------------
            # Step 8 — Mark EXECUTING
            # ---------------------------------

            trade_lifecycle_manager.set_state(
                symbol=symbol,
                state=(
                    trade_lifecycle_manager
                    .STATE_EXECUTING
                ),
                metadata={
                    "direction": (
                        str(direction).upper()
                    ),
                    "lot_size": float(lot_size),
                    "stop_loss": float(stop_loss),
                    "take_profit": float(take_profit)
                }
            )

            # ---------------------------------
            # Step 9 — LIVE EXECUTION
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

            execution_success = (
                execution_result.get(
                    "success",
                    False
                )
            )

            # ---------------------------------
            # Step 10 — Execution failed
            # ---------------------------------

            if not execution_success:

                trade_lifecycle_manager.set_state(
                    symbol=symbol,
                    state=(
                        trade_lifecycle_manager
                        .STATE_FAILED
                    ),
                    metadata={
                        "execution": execution_result
                    }
                )

                return {
                    "success": False,
                    "message": (
                        execution_result.get(
                            "message",
                            "Execution failed."
                        )
                    ),
                    "data": {
                        "stage": "LIVE_EXECUTION",
                        "dry_run": False,
                        "executed": False,
                        "execution": execution_result,
                        "lifecycle_state": "FAILED"
                    }
                }

            # ---------------------------------
            # Step 11 — Recover actual MT5 state
            # ---------------------------------
            #
            # Do not assume the position exists
            # merely because order_send succeeded.
            # MT5 remains the source of truth.
            # ---------------------------------

            recovery_result = (
                trade_lifecycle_manager
                .recover_state(symbol)
            )

            if not recovery_result["success"]:

                return {
                    "success": False,
                    "message": (
                        "Trade executed, but lifecycle "
                        "state recovery failed."
                    ),
                    "data": {
                        "stage": "STATE_RECOVERY",
                        "dry_run": False,
                        "executed": True,
                        "execution": execution_result,
                        "recovery": recovery_result
                    }
                }

            recovered_state = (
                recovery_result["data"]["state"]
            )

            # ---------------------------------
            # Step 12 — Verify OPEN state
            # ---------------------------------

            if (
                recovered_state
                != trade_lifecycle_manager.STATE_OPEN
            ):

                trade_lifecycle_manager.set_state(
                    symbol=symbol,
                    state=(
                        trade_lifecycle_manager
                        .STATE_FAILED
                    ),
                    metadata={
                        "reason": (
                            "Execution succeeded but "
                            "no JD-Algo open position "
                            "was found in MT5."
                        ),
                        "execution": execution_result
                    }
                )

                return {
                    "success": False,
                    "message": (
                        "Execution succeeded, but "
                        "MT5 position verification failed."
                    ),
                    "data": {
                        "stage": (
                            "POSITION_VERIFICATION"
                        ),
                        "dry_run": False,
                        "executed": True,
                        "execution": execution_result,
                        "recovery": recovery_result
                    }
                }

            # ---------------------------------
            # Step 13 — Success
            # ---------------------------------

            return {
                "success": True,
                "message": (
                    execution_result.get(
                        "message",
                        "Market order executed successfully."
                    )
                ),
                "data": {
                    "stage": "LIVE_EXECUTION",
                    "dry_run": False,
                    "executed": True,
                    "execution": execution_result,
                    "lifecycle": recovery_result["data"]
                }
            }

        except Exception as error:

            # ---------------------------------
            # Mark FAILED where possible
            # ---------------------------------

            if not dry_run:

                try:

                    trade_lifecycle_manager.set_state(
                        symbol=symbol,
                        state=(
                            trade_lifecycle_manager
                            .STATE_FAILED
                        ),
                        metadata={
                            "error": str(error)
                        }
                    )

                except Exception:
                    pass

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

            # ---------------------------------
            # Always release execution lock
            # ---------------------------------

            if execution_lock_acquired:

                trade_lifecycle_manager \
                    .release_execution_lock()

            connector.disconnect()


execution_controller = ExecutionController()