from .risk_calculator import risk_calculator
from .lot_size_calculator import lot_size_calculator
from .stop_loss_engine import stop_loss_engine
from .take_profit_engine import take_profit_engine
from .trade_validator import trade_validator


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

    def calculate_take_profit(
        self,
        entry_price,
        stop_loss,
        direction,
        risk_reward=None
    ):

        return take_profit_engine.calculate(
            entry_price,
            stop_loss,
            direction,
            risk_reward
        )

    def validate_trade(
        self,
        direction,
        entry_price,
        stop_loss,
        take_profit,
        lot_size
    ):

        return trade_validator.validate(
            direction,
            entry_price,
            stop_loss,
            take_profit,
            lot_size
        )

risk_engine = RiskEngine()