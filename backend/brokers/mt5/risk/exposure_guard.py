import math

import MetaTrader5 as mt5

from connector import connector


class ExposureGuard:

    # --------------------------------------------------
    # Safety configuration
    # --------------------------------------------------

    MAX_LOT_SIZE = 5.00
    MAX_RISK_PERCENT = 1.00

    # Maximum percentage of current free margin that
    # one new trade may consume.
    MAX_MARGIN_USAGE_PERCENT = 20.0

    # Small tolerance for rounding differences between
    # our calculations and MT5.
    RISK_TOLERANCE_PERCENT = 5.0

    JD_ALGO_MAGIC = 10001

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _normalize_direction(self, direction):

        direction = str(direction).strip().upper()

        if direction not in ("BUY", "SELL"):
            return None

        return direction

    def _normalize_volume(
        self,
        volume,
        volume_min,
        volume_max,
        volume_step
    ):

        if volume_step <= 0:
            return None

        volume = float(volume)

        steps = math.floor(
            (volume / volume_step) + 1e-12
        )

        normalized = steps * volume_step

        normalized = max(
            volume_min,
            min(normalized, volume_max)
        )

        decimals = 0

        step_text = (
            f"{volume_step:.10f}"
            .rstrip("0")
            .rstrip(".")
        )

        if "." in step_text:
            decimals = len(
                step_text.split(".")[1]
            )

        return round(
            normalized,
            decimals
        )

    # --------------------------------------------------
    # Validate proposed exposure
    # --------------------------------------------------

    def validate(
        self,
        symbol,
        direction,
        lot_size,
        entry_price,
        stop_loss,
        risk_percent
    ):

        direction = self._normalize_direction(
            direction
        )

        if direction is None:

            return {
                "success": False,
                "message": "Invalid trade direction.",
                "data": {
                    "allowed": False,
                    "failed_checks": [
                        "direction"
                    ]
                }
            }

        try:

            lot_size = float(lot_size)
            entry_price = float(entry_price)
            stop_loss = float(stop_loss)
            risk_percent = float(risk_percent)

        except (TypeError, ValueError):

            return {
                "success": False,
                "message": (
                    "Invalid exposure guard parameters."
                ),
                "data": {
                    "allowed": False
                }
            }

        status = connector.connect()

        if not status["success"]:
            return status

        try:

            account = mt5.account_info()
            info = mt5.symbol_info(symbol)

            if account is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to retrieve MT5 "
                        "account information."
                    ),
                    "mt5_error": mt5.last_error()
                }

            if info is None:

                return {
                    "success": False,
                    "message": (
                        f"Symbol '{symbol}' not found."
                    )
                }

            if not info.visible:

                if not mt5.symbol_select(
                    symbol,
                    True
                ):

                    return {
                        "success": False,
                        "message": (
                            "Unable to select symbol."
                        )
                    }

            # ------------------------------------------
            # Broker volume normalization
            # ------------------------------------------

            normalized_volume = (
                self._normalize_volume(
                    volume=lot_size,
                    volume_min=float(
                        info.volume_min
                    ),
                    volume_max=float(
                        info.volume_max
                    ),
                    volume_step=float(
                        info.volume_step
                    )
                )
            )

            if normalized_volume is None:

                return {
                    "success": False,
                    "message": (
                        "Unable to normalize volume."
                    )
                }

            # ------------------------------------------
            # Direction / SL relationship
            # ------------------------------------------

            if direction == "BUY":

                sl_direction_valid = (
                    stop_loss < entry_price
                )

                order_type = mt5.ORDER_TYPE_BUY

            else:

                sl_direction_valid = (
                    stop_loss > entry_price
                )

                order_type = mt5.ORDER_TYPE_SELL

            # ------------------------------------------
            # Requested risk amount
            # ------------------------------------------

            balance = float(account.balance)
            equity = float(account.equity)
            free_margin = float(
                account.margin_free
            )

            requested_risk_amount = (
                balance
                * risk_percent
                / 100.0
            )

            # ------------------------------------------
            # MT5-native loss verification
            #
            # Calculate P/L if price moves from entry
            # directly to the proposed stop loss.
            # ------------------------------------------

            calculated_profit = (
                mt5.order_calc_profit(
                    order_type,
                    symbol,
                    normalized_volume,
                    entry_price,
                    stop_loss
                )
            )

            if calculated_profit is None:

                return {
                    "success": False,
                    "message": (
                        "MT5 order_calc_profit failed."
                    ),
                    "mt5_error": mt5.last_error()
                }

            mt5_stop_loss_amount = abs(
                float(calculated_profit)
            )

            # ------------------------------------------
            # MT5-native margin requirement
            # ------------------------------------------

            required_margin = (
                mt5.order_calc_margin(
                    order_type,
                    symbol,
                    normalized_volume,
                    entry_price
                )
            )

            if required_margin is None:

                return {
                    "success": False,
                    "message": (
                        "MT5 order_calc_margin failed."
                    ),
                    "mt5_error": mt5.last_error()
                }

            required_margin = float(
                required_margin
            )

            # ------------------------------------------
            # Safety limits
            # ------------------------------------------

            maximum_allowed_risk = (
                requested_risk_amount
                * (
                    1.0
                    + (
                        self.RISK_TOLERANCE_PERCENT
                        / 100.0
                    )
                )
            )

            if free_margin > 0:

                margin_usage_percent = (
                    required_margin
                    / free_margin
                    * 100.0
                )

            else:

                margin_usage_percent = (
                    float("inf")
                )

            checks = {
                "direction": (
                    direction in ("BUY", "SELL")
                ),

                "stop_loss_direction": (
                    sl_direction_valid
                ),

                "risk_percent": (
                    risk_percent > 0
                    and risk_percent
                    <= self.MAX_RISK_PERCENT
                ),

                "broker_min_volume": (
                    normalized_volume
                    >= float(info.volume_min)
                ),

                "broker_max_volume": (
                    normalized_volume
                    <= float(info.volume_max)
                ),

                "configured_max_lot": (
                    normalized_volume
                    <= self.MAX_LOT_SIZE
                ),

                "mt5_stop_loss_risk": (
                    mt5_stop_loss_amount
                    <= maximum_allowed_risk
                ),

                "free_margin": (
                    free_margin > required_margin
                ),

                "margin_usage": (
                    margin_usage_percent
                    <= self.MAX_MARGIN_USAGE_PERCENT
                )
            }

            failed_checks = [
                name
                for name, passed
                in checks.items()
                if not passed
            ]

            allowed = (
                len(failed_checks) == 0
            )

            return {
                "success": allowed,
                "message": (
                    "Exposure safety checks passed."
                    if allowed
                    else
                    "Trade blocked by exposure safety guard."
                ),
                "data": {
                    "allowed": allowed,

                    "symbol": symbol,
                    "direction": direction,

                    "requested_lot_size": (
                        lot_size
                    ),
                    "normalized_lot_size": (
                        normalized_volume
                    ),

                    "entry_price": entry_price,
                    "stop_loss": stop_loss,

                    "account": {
                        "balance": round(
                            balance,
                            2
                        ),
                        "equity": round(
                            equity,
                            2
                        ),
                        "free_margin": round(
                            free_margin,
                            2
                        )
                    },

                    "risk": {
                        "risk_percent": (
                            risk_percent
                        ),
                        "requested_risk_amount": (
                            round(
                                requested_risk_amount,
                                2
                            )
                        ),
                        "mt5_stop_loss_amount": (
                            round(
                                mt5_stop_loss_amount,
                                2
                            )
                        ),
                        "maximum_allowed_risk": (
                            round(
                                maximum_allowed_risk,
                                2
                            )
                        ),
                        "tolerance_percent": (
                            self
                            .RISK_TOLERANCE_PERCENT
                        )
                    },

                    "margin": {
                        "required_margin": (
                            round(
                                required_margin,
                                2
                            )
                        ),
                        "margin_usage_percent": (
                            round(
                                margin_usage_percent,
                                2
                            )
                        ),
                        "maximum_usage_percent": (
                            self
                            .MAX_MARGIN_USAGE_PERCENT
                        )
                    },

                    "limits": {
                        "configured_max_lot": (
                            self.MAX_LOT_SIZE
                        ),
                        "broker_min_lot": float(
                            info.volume_min
                        ),
                        "broker_max_lot": float(
                            info.volume_max
                        ),
                        "broker_volume_step": float(
                            info.volume_step
                        ),
                        "maximum_risk_percent": (
                            self.MAX_RISK_PERCENT
                        )
                    },

                    "checks": checks,
                    "failed_checks": (
                        failed_checks
                    )
                }
            }

        finally:

            connector.disconnect()


exposure_guard = ExposureGuard()