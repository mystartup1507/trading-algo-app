from strategies.strategy_manager import StrategyManager
from services.market_snapshot_builder import market_snapshot_builder


class DecisionEngine:

    def __init__(self):

        self.manager = StrategyManager()

        self.strategies = [
            "ema_rsi_adx",
            "ema_crossover",
            "macd",
            "supertrend",
            "bollinger",
            "ichimoku"
        ]

    def analyze(self, symbol, timeframe):

        results = []

        buy_score = 0
        sell_score = 0
        hold_score = 0

        for strategy_name in self.strategies:

            strategy = self.manager.get_strategy(strategy_name)

            if strategy is None:
                continue

            #
            # EMA+RSI+ADX uses Market Snapshot
            #
            if strategy_name == "ema_rsi_adx":

                snapshot = market_snapshot_builder.build(
                    symbol,
                    timeframe
                )

                result = strategy.generate_signal(snapshot)

            #
            # Other strategies use symbol + timeframe
            #
            else:

                result = strategy.generate_signal(
                    symbol,
                    timeframe
                )

            if not result["success"]:
                continue

            data = result["data"]

            results.append(data)

            confidence = data.get("confidence", 0)
            signal = data.get("signal", "HOLD")

            if signal == "BUY":
                buy_score += confidence

            elif signal == "SELL":
                sell_score += confidence

            else:
                hold_score += confidence

        #
        # Final Decision
        #
        final_signal = "HOLD"
        confidence = hold_score

        if buy_score > sell_score and buy_score > hold_score:
            final_signal = "BUY"
            confidence = buy_score

        elif sell_score > buy_score and sell_score > hold_score:
            final_signal = "SELL"
            confidence = sell_score

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,

                "final_signal": final_signal,

                "buy_score": buy_score,
                "sell_score": sell_score,
                "hold_score": hold_score,

                "confidence": confidence,

                "strategies": results
            }
        }


decision_engine = DecisionEngine()