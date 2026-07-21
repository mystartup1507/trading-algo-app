from .ema_rsi_adx_strategy import EmaRsiAdxStrategy


class StrategyManager:

    def __init__(self):
        self._strategies = {
            "ema_rsi_adx": EmaRsiAdxStrategy(),
        }

    def get_strategy(self, strategy_name="ema_rsi_adx"):

        strategy = self._strategies.get(strategy_name)

        if strategy is None:
            raise ValueError(
                f"Unknown strategy: {strategy_name}"
            )

        return strategy