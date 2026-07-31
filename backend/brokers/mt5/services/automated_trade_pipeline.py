from decision.decision_engine import decision_engine
from risk.risk_engine import risk_engine
from risk.exposure_guard import exposure_guard
from trade_execution.execution_controller import execution_controller


class AutomatedTradePipeline:

    DEFAULT_RISK_PERCENT = 1.0
    DEFAULT_ATR_MULTIPLIER = 2.0
    DEFAULT_RISK_REWARD = 2.0

    def run(
        self,
        symbol,
        timeframe,
        risk_percent=None,
        atr_multiplier=None,
        risk_reward=None,
        dry_run=True,
        confirmation_token=None
    ):

        # --------------------------------------------------
        # Defaults
        # --------------------------------------------------

        if risk_percent is None:
            risk_percent = self.DEFAULT_RISK_PERCENT

        if atr_multiplier is None:
            atr_multiplier = self.DEFAULT_ATR_MULTIPLIER

        if risk_reward is None:
            risk_reward = self.DEFAULT_RISK_REWARD

        try:
            risk_percent = float(risk_percent)
            atr_multiplier = float(atr_multiplier)
            risk_reward = float(risk_reward)

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": "Invalid pipeline parameters.",
                "data": {
                    "stage": "INPUT_VALIDATION",
                    "executed": False
                }
            }

        # --------------------------------------------------
        # Basic parameter validation
        # --------------------------------------------------

        if risk_percent <= 0:

            return {
                "success": False,
                "message": (
                    "Risk percent must be greater "
                    "than zero."
                ),
                "data": {
                    "stage": "INPUT_VALIDATION",
                    "executed": False
                }
            }

        if atr_multiplier <= 0:

            return {
                "success": False,
                "message": (
                    "ATR multiplier must be greater "
                    "than zero."
                ),
                "data": {
                    "stage": "INPUT_VALIDATION",
                    "executed": False
                }
            }

        if risk_reward <= 0:

            return {
                "success": False,
                "message": (
                    "Risk/reward must be greater "
                    "than zero."
                ),
                "data": {
                    "stage": "INPUT_VALIDATION",
                    "executed": False
                }
            }

        try:

            # ==================================================
            # STEP 1 — DECISION ENGINE
            # ==================================================

            decision_result = decision_engine.analyze(
                symbol,
                timeframe
            )

            if not decision_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": "Decision engine failed.",
                    "data": {
                        "stage": "DECISION",
                        "executed": False,
                        "decision": decision_result
                    }
                }

            decision_data = decision_result.get(
                "data",
                {}
            )

            direction = str(
                decision_data.get(
                    "final_signal",
                    "HOLD"
                )
            ).upper()

            # ==================================================
            # STEP 2 — HOLD = NO TRADE
            # ==================================================

            if direction == "HOLD":

                return {
                    "success": True,
                    "message": (
                        "Decision engine returned HOLD. "
                        "No trade was generated."
                    ),
                    "data": {
                        "stage": "NO_TRADE",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "signal": "HOLD",
                        "executed": False,
                        "decision": decision_data
                    }
                }

            if direction not in (
                "BUY",
                "SELL"
            ):

                return {
                    "success": False,
                    "message": (
                        "Decision engine returned "
                        "an invalid trading direction."
                    ),
                    "data": {
                        "stage": "DECISION",
                        "signal": direction,
                        "executed": False,
                        "decision": decision_data
                    }
                }

            # ==================================================
            # STEP 3 — ATR STOP LOSS
            # ==================================================

            stop_result = (
                risk_engine.calculate_stop_loss(
                    symbol=symbol,
                    timeframe=timeframe,
                    direction=direction,
                    multiplier=atr_multiplier
                )
            )

            if not stop_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Stop-loss calculation failed."
                    ),
                    "data": {
                        "stage": "STOP_LOSS",
                        "executed": False,
                        "decision": decision_data,
                        "stop_loss": stop_result
                    }
                }

            stop_data = stop_result.get(
                "data",
                {}
            )

            entry_price = float(
                stop_data["entry_price"]
            )

            stop_loss = float(
                stop_data["stop_loss"]
            )

            stop_loss_pips = float(
                stop_data["distance_pips"]
            )

            # ==================================================
            # STEP 4 — MT5-NATIVE LOT SIZE
            # ==================================================

            lot_result = (
                risk_engine.calculate_lot_size(
                    symbol=symbol,
                    risk_percent=risk_percent,
                    stop_loss_pips=stop_loss_pips
                )
            )

            if not lot_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Lot-size calculation failed."
                    ),
                    "data": {
                        "stage": "LOT_SIZE",
                        "executed": False,
                        "decision": decision_data,
                        "stop_loss": stop_data,
                        "lot_size": lot_result
                    }
                }

            lot_data = lot_result.get(
                "data",
                {}
            )

            lot_size = float(
                lot_data["lot_size"]
            )

            # ==================================================
            # STEP 5 — TAKE PROFIT
            # ==================================================

            tp_result = (
                risk_engine.calculate_take_profit(
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    direction=direction,
                    risk_reward=risk_reward
                )
            )

            if not tp_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Take-profit calculation failed."
                    ),
                    "data": {
                        "stage": "TAKE_PROFIT",
                        "executed": False,
                        "decision": decision_data,
                        "stop_loss": stop_data,
                        "lot_size": lot_data,
                        "take_profit": tp_result
                    }
                }

            tp_data = tp_result.get(
                "data",
                {}
            )

            take_profit = float(
                tp_data["take_profit"]
            )

            # ==================================================
            # STEP 6 — TRADE VALIDATOR
            # ==================================================

            trade_validation = (
                risk_engine.validate_trade(
                    direction=direction,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    lot_size=lot_size
                )
            )

            if not trade_validation.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Trade blocked by risk validation."
                    ),
                    "data": {
                        "stage": "RISK_VALIDATION",
                        "executed": False,
                        "decision": decision_data,
                        "entry_price": entry_price,
                        "stop_loss": stop_data,
                        "take_profit": tp_data,
                        "lot_size": lot_data,
                        "validation": trade_validation
                    }
                }

            # ==================================================
            # STEP 7 — EXPOSURE SAFETY GUARD
            #
            # Independent MT5-native verification:
            #
            # - maximum configured lot
            # - actual monetary SL risk
            # - maximum risk percentage
            # - required margin
            # - free margin
            # - margin usage
            #
            # Unsafe trades are BLOCKED.
            # They are never silently resized.
            # ==================================================

            exposure_result = (
                exposure_guard.validate(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    risk_percent=risk_percent
                )
            )

            if not exposure_result.get(
                "success",
                False
            ):

                return {
                    "success": False,
                    "message": (
                        "Trade blocked by risk and "
                        "exposure safety guard."
                    ),
                    "data": {
                        "stage": "EXPOSURE_GUARD",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "direction": direction,
                        "dry_run": bool(dry_run),
                        "executed": False,

                        "decision": decision_data,

                        "risk": {
                            "risk_percent": (
                                risk_percent
                            ),
                            "entry_price": (
                                entry_price
                            ),
                            "stop_loss": (
                                stop_loss
                            ),
                            "stop_loss_pips": (
                                stop_loss_pips
                            ),
                            "take_profit": (
                                take_profit
                            ),
                            "risk_reward": (
                                risk_reward
                            ),
                            "lot_size": (
                                lot_size
                            )
                        },

                        "stop_loss_engine": (
                            stop_data
                        ),

                        "lot_size_engine": (
                            lot_data
                        ),

                        "take_profit_engine": (
                            tp_data
                        ),

                        "trade_validation": (
                            trade_validation.get(
                                "data",
                                {}
                            )
                        ),

                        "exposure_guard": (
                            exposure_result
                        )
                    }
                }

            # ==================================================
            # STEP 8 — EXECUTION CONTROLLER
            #
            # Only trades passing every previous layer can
            # reach this point.
            #
            # The public automatic-trade test endpoint must
            # continue passing dry_run=True.
            # ==================================================

            execution_result = (
                execution_controller.execute(
                    symbol=symbol,
                    direction=direction,
                    lot_size=lot_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    dry_run=bool(dry_run),
                    confirmation_token=(
                        confirmation_token
                    )
                )
            )

            execution_success = (
                execution_result.get(
                    "success",
                    False
                )
            )

            executed = (
                execution_result
                .get("data", {})
                .get("executed", False)
            )

            # ==================================================
            # STEP 9 — UNIFIED PIPELINE RESULT
            # ==================================================

            return {
                "success": execution_success,
                "message": execution_result.get(
                    "message",
                    (
                        "Automatic trade pipeline "
                        "completed."
                    )
                ),
                "data": {
                    "stage": (
                        "EXECUTION"
                        if execution_success
                        else "EXECUTION_BLOCKED"
                    ),

                    "symbol": symbol,
                    "timeframe": timeframe,
                    "direction": direction,

                    "dry_run": bool(
                        dry_run
                    ),

                    "executed": executed,

                    "decision": (
                        decision_data
                    ),

                    "risk": {
                        "risk_percent": (
                            risk_percent
                        ),
                        "entry_price": (
                            entry_price
                        ),
                        "stop_loss": (
                            stop_loss
                        ),
                        "stop_loss_pips": (
                            stop_loss_pips
                        ),
                        "take_profit": (
                            take_profit
                        ),
                        "risk_reward": (
                            risk_reward
                        ),
                        "lot_size": (
                            lot_size
                        )
                    },

                    "stop_loss_engine": (
                        stop_data
                    ),

                    "lot_size_engine": (
                        lot_data
                    ),

                    "take_profit_engine": (
                        tp_data
                    ),

                    "trade_validation": (
                        trade_validation.get(
                            "data",
                            {}
                        )
                    ),

                    "exposure_guard": (
                        exposure_result.get(
                            "data",
                            {}
                        )
                    ),

                    "execution": (
                        execution_result
                    )
                }
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Automated Trade Pipeline error: "
                    f"{str(error)}"
                ),
                "data": {
                    "stage": "ERROR",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "dry_run": bool(dry_run),
                    "executed": False
                }
            }


automated_trade_pipeline = AutomatedTradePipeline()