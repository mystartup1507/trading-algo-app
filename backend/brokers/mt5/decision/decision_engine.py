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

        buy_count = 0
        sell_count = 0
        hold_count = 0

        for strategy_name in self.strategies:

            strategy = self.manager.get_strategy(
                strategy_name
            )

            if strategy is None:
                continue

            # ------------------------------------------
            # EMA + RSI + ADX uses Market Snapshot
            # ------------------------------------------

            if strategy_name == "ema_rsi_adx":

                snapshot = market_snapshot_builder.build(
                    symbol,
                    timeframe
                )

                result = strategy.generate_signal(
                    snapshot
                )

            # ------------------------------------------
            # Other strategies use symbol + timeframe
            # ------------------------------------------

            else:

                result = strategy.generate_signal(
                    symbol,
                    timeframe
                )

            if not result["success"]:
                continue

            data = result["data"]

            results.append(data)

            try:
                confidence = float(
                    data.get("confidence", 0)
                )

            except (TypeError, ValueError):
                confidence = 0.0

            # Keep individual strategy confidence
            # inside the expected percentage range.

            confidence = max(
                0.0,
                min(confidence, 100.0)
            )

            signal = str(
                data.get(
                    "signal",
                    "HOLD"
                )
            ).upper()

            if signal == "BUY":

                buy_score += confidence
                buy_count += 1

            elif signal == "SELL":

                sell_score += confidence
                sell_count += 1

            else:

                hold_score += confidence
                hold_count += 1

        # ----------------------------------------------
        # Final decision
        #
        # Cumulative scores continue to determine
        # which side wins.
        # ----------------------------------------------

        final_signal = "HOLD"
        winning_score = hold_score
        winning_count = hold_count

        if (
            buy_score > sell_score
            and buy_score > hold_score
        ):

            final_signal = "BUY"
            winning_score = buy_score
            winning_count = buy_count

        elif (
            sell_score > buy_score
            and sell_score > hold_score
        ):

            final_signal = "SELL"
            winning_score = sell_score
            winning_count = sell_count

        # ----------------------------------------------
        # Normalized final confidence
        #
        # Average confidence of strategies that voted
        # for the winning signal.
        # ----------------------------------------------

        if winning_count > 0:

            confidence = (
                winning_score / winning_count
            )

        else:

            confidence = 0.0

        confidence = round(
            max(
                0.0,
                min(confidence, 100.0)
            ),
            2
        )

        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,

                "final_signal": final_signal,

                # Raw voting scores are deliberately
                # retained for transparency.
                "buy_score": round(
                    buy_score,
                    2
                ),
                "sell_score": round(
                    sell_score,
                    2
                ),
                "hold_score": round(
                    hold_score,
                    2
                ),

                # Normalized 0-100 confidence.
                "confidence": confidence,

                "vote_counts": {
                    "buy": buy_count,
                    "sell": sell_count,
                    "hold": hold_count
                },

                "strategies": results
            }
        }


decision_engine = DecisionEngine()