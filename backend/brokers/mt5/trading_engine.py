from strategies.strategy_manager import StrategyManager
from services.market_snapshot_builder import market_snapshot_builder


class TradingEngine:

    def __init__(self):

        self.strategy_manager = StrategyManager()

    def generate_signal(
        self,
        symbol,
        timeframe,
        strategy_name="ema_rsi_adx"
    ):

        snapshot = market_snapshot_builder.build(
            symbol,
            timeframe
        )

        strategy = self.strategy_manager.get_strategy(
            strategy_name
        )

        return strategy.generate_signal(snapshot)

trading_engine = TradingEngine()