from .risk_calculator import risk_calculator
from .lot_size_calculator import lot_size_calculator
from .stop_loss_engine import stop_loss_engine


class RiskEngine:

    def calculate_risk(self, risk_percent=None):

        return risk_calculator.calculate(risk_percent)

    def calculate_lot_size(
        self,
        symbol,
        risk_percent,
        stop_loss_pips
    ):

        return lot_size_calculator.calculate(
            symbol,
            risk_percent,
            stop_loss_pips
        )

    def calculate_stop_loss(
        self,
        symbol,
        timeframe,
        direction,
        multiplier=None
    ):

        return stop_loss_engine.atr_stop_loss(
            symbol,
            timeframe,
            direction,
            multiplier
        )

risk_engine = RiskEngine()