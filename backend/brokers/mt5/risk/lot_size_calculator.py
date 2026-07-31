import math

import MetaTrader5 as mt5

from connector import connector
from .risk_calculator import risk_calculator


class LotSizeCalculator:

    def calculate(
        self,
        symbol,
        risk_percent,
        stop_loss_pips
    ):

        # ----------------------------------------------
        # Validate input
        # ----------------------------------------------

        try:
            risk_percent = float(risk_percent)
            stop_loss_pips = float(stop_loss_pips)

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": (
                    "risk_percent and stop_loss_pips "
                    "must be valid numbers."
                )
            }

        if risk_percent <= 0:

            return {
                "success": False,
                "message": (
                    "Risk percent must be greater "
                    "than zero."
                )
            }

        if stop_loss_pips <= 0:

            return {
                "success": False,
                "message": (
                    "Stop-loss pips must be greater "
                    "than zero."
                )
            }

        # ----------------------------------------------
        # Calculate permitted monetary risk
        # ----------------------------------------------

        risk = risk_calculator.calculate(
            risk_percent
        )

        if not risk["success"]:
            return risk

        risk_amount = float(
            risk["data"]["max_risk_amount"]
        )

        balance = float(
            risk["data"]["balance"]
        )

        # ----------------------------------------------
        # Connect to MT5
        # ----------------------------------------------

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            symbol_info = mt5.symbol_info(
                symbol
            )

            if symbol_info is None:

                return {
                    "success": False,
                    "message": (
                        f"Symbol '{symbol}' not found."
                    )
                }

            if not symbol_info.visible:

                if not mt5.symbol_select(
                    symbol,
                    True
                ):

                    return {
                        "success": False,
                        "message": (
                            f"Unable to select "
                            f"symbol '{symbol}'."
                        )
                    }

            tick = mt5.symbol_info_tick(
                symbol
            )

            if tick is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to retrieve live price."
                    )
                }

            # ------------------------------------------
            # Determine pip size
            #
            # Standard FX:
            #
            # 5-digit quote:
            # point = 0.00001
            # pip   = 0.00010
            #
            # 3-digit quote:
            # point = 0.001
            # pip   = 0.01
            #
            # Otherwise use point directly.
            # ------------------------------------------

            digits = int(
                symbol_info.digits
            )

            point = float(
                symbol_info.point
            )

            if digits in (3, 5):
                pip_size = point * 10.0
            else:
                pip_size = point

            stop_distance_price = (
                stop_loss_pips
                * pip_size
            )

            # ------------------------------------------
            # Use MT5-native P/L calculation
            #
            # Calculate the loss for exactly 1 lot.
            # This avoids manually assuming contract
            # size / tick-value behavior.
            # ------------------------------------------

            entry_price = float(
                tick.ask
            )

            stop_price = (
                entry_price
                - stop_distance_price
            )

            loss_one_lot = (
                mt5.order_calc_profit(
                    mt5.ORDER_TYPE_BUY,
                    symbol,
                    1.0,
                    entry_price,
                    stop_price
                )
            )

            if loss_one_lot is None:

                return {
                    "success": False,
                    "message": (
                        "MT5 could not calculate "
                        "one-lot stop-loss risk."
                    ),
                    "mt5_error": (
                        mt5.last_error()
                    )
                }

            loss_per_lot = abs(
                float(loss_one_lot)
            )

            if loss_per_lot <= 0:

                return {
                    "success": False,
                    "message": (
                        "Invalid MT5 loss-per-lot "
                        "calculation."
                    )
                }

            # ------------------------------------------
            # Raw risk-based volume
            # ------------------------------------------

            raw_lot_size = (
                risk_amount
                / loss_per_lot
            )

            volume_step = float(
                symbol_info.volume_step
            )

            min_volume = float(
                symbol_info.volume_min
            )

            max_volume = float(
                symbol_info.volume_max
            )

            if volume_step <= 0:

                return {
                    "success": False,
                    "message": (
                        "Invalid broker volume step."
                    )
                }

            # ------------------------------------------
            # Round DOWN, never up.
            #
            # Rounding up could exceed the requested
            # monetary risk.
            # ------------------------------------------

            steps = math.floor(
                (
                    raw_lot_size
                    / volume_step
                )
                + 1e-12
            )

            lot_size = (
                steps
                * volume_step
            )

            # ------------------------------------------
            # Reject rather than force minimum lot
            #
            # If the risk model produces less than the
            # broker minimum, forcing min_volume could
            # exceed the requested risk.
            # ------------------------------------------

            if lot_size < min_volume:

                return {
                    "success": False,
                    "message": (
                        "Calculated risk-based lot size "
                        "is below broker minimum."
                    ),
                    "data": {
                        "raw_lot_size": (
                            raw_lot_size
                        ),
                        "broker_min_lot": (
                            min_volume
                        )
                    }
                }

            lot_size = min(
                lot_size,
                max_volume
            )

            # ------------------------------------------
            # Final native MT5 risk verification
            # ------------------------------------------

            verified_loss = (
                loss_per_lot
                * lot_size
            )

            return {
                "success": True,
                "message": (
                    "MT5-native lot size "
                    "calculated successfully."
                ),
                "data": {
                    "symbol": symbol,
                    "balance": round(
                        balance,
                        2
                    ),
                    "risk_percent": (
                        risk_percent
                    ),
                    "risk_amount": round(
                        risk_amount,
                        2
                    ),
                    "stop_loss_pips": (
                        stop_loss_pips
                    ),
                    "pip_size": pip_size,
                    "stop_distance_price": (
                        stop_distance_price
                    ),
                    "loss_per_lot": round(
                        loss_per_lot,
                        2
                    ),
                    "raw_lot_size": round(
                        raw_lot_size,
                        4
                    ),
                    "lot_size": round(
                        lot_size,
                        2
                    ),
                    "verified_risk_amount": (
                        round(
                            verified_loss,
                            2
                        )
                    ),
                    "volume_step": (
                        volume_step
                    ),
                    "volume_min": (
                        min_volume
                    ),
                    "volume_max": (
                        max_volume
                    ),
                    "calculation_method": (
                        "MT5_ORDER_CALC_PROFIT"
                    )
                }
            }

        finally:

            connector.disconnect()


lot_size_calculator = LotSizeCalculator()