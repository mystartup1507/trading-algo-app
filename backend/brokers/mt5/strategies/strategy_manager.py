from .ema_rsi_adx_strategy import EmaRsiAdxStrategy
from .ema_crossover_strategy import EmaCrossoverStrategy
from .macd_strategy import MacdStrategy
from .supertrend_strategy import SuperTrendStrategy
from .bollinger_strategy import BollingerStrategy
from .ichimoku_strategy import IchimokuStrategy


class StrategyManager:

    def __init__(self):

        self._strategies = {
            "ema_rsi_adx": EmaRsiAdxStrategy(),
            "ema_crossover": EmaCrossoverStrategy(),
            "macd": MacdStrategy(),
            "supertrend": SuperTrendStrategy(),
            "bollinger": BollingerStrategy(),
            "ichimoku": IchimokuStrategy(),
        }

    def get_strategy(self, strategy_name="ema_rsi_adx"):

        strategy = self._strategies.get(strategy_name)

        if strategy is None:
            raise ValueError(
                f"Unknown strategy: {strategy_name}"
            )

        return strategy

    def get_all_strategies(self):

        return self._strategies