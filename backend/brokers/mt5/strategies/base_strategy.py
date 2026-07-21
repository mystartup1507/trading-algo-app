from abc import ABC, abstractmethod


class BaseStrategy(ABC):

    @abstractmethod
    def generate_signal(self, symbol, timeframe):
        """
        Every trading strategy must implement this method.

        Returns:
            {
                "success": True,
                "data": {
                    "signal": "BUY" | "SELL" | "HOLD"
                }
            }
        """
        pass