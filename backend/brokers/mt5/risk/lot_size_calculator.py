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

        

        risk = risk_calculator.calculate(risk_percent)

        if not risk["success"]:

            connector.disconnect()

            return risk

        risk_amount = risk["data"]["max_risk_amount"]
        balance = risk["data"]["balance"]

        status = connector.connect()

        if not status["success"]:
            return status

        print("SYMBOL RECEIVED:", repr(symbol))

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:

            connector.disconnect()

            return {
                "success": False,
                "message": "Symbol not found."
            }

        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        volume_step = symbol_info.volume_step
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max

        connector.disconnect()

        if tick_value <= 0 or tick_size <= 0:

            return {
                "success": False,
                "message": "Invalid symbol properties."
            }

        stop_loss_price = stop_loss_pips * tick_size

        loss_per_lot = (
            stop_loss_price / tick_size
        ) * tick_value

        if loss_per_lot <= 0:

            return {
                "success": False,
                "message": "Invalid stop loss."
            }

        lot_size = risk_amount / loss_per_lot

        lot_size = round(
            lot_size / volume_step
        ) * volume_step

        lot_size = max(
            min_volume,
            min(
                lot_size,
                max_volume
            )
        )

        return {
            "success": True,
            "message": "Lot size calculated successfully.",
            "data": {
                "symbol": symbol,
                "balance": balance,
                "risk_percent": risk_percent,
                "risk_amount": round(risk_amount, 2),
                "stop_loss_pips": stop_loss_pips,
                "lot_size": round(lot_size, 2),
                "tick_value": tick_value,
                "tick_size": tick_size,
                "volume_step": volume_step
            }
        }


lot_size_calculator = LotSizeCalculator()