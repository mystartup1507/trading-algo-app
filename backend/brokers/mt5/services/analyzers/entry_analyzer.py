from .analysis_result import AnalysisResult


class EntryAnalyzer:

    def analyze(self, snapshot):

        result = AnalysisResult()

        #
        # Default
        #
        result.state = "HOLD"
        result.score = 0
        result.confidence = 0.0
        result.reason = "No valid trading setup."

        #
        # BUY
        #
        if (
            snapshot.trend.state == "UPTREND"
            and snapshot.momentum.state == "STRONG"
            and snapshot.volatility.state == "NORMAL"
        ):

            result.state = "BUY"
            result.score = 100
            result.confidence = (
                snapshot.trend.confidence
                * snapshot.momentum.confidence
                * snapshot.volatility.confidence
            ) ** (1 / 3)

            result.reason = (
                "Trend, Momentum and Volatility confirmed."
            )

            return result

        #
        # SELL
        #
        if (
            snapshot.trend.state == "DOWNTREND"
            and snapshot.momentum.state == "STRONG"
            and snapshot.volatility.state == "NORMAL"
        ):

            result.state = "SELL"
            result.score = 100
            result.confidence = (
                snapshot.trend.confidence
                * snapshot.momentum.confidence
                * snapshot.volatility.confidence
            ) ** (1 / 3)

            result.reason = (
                "Trend, Momentum and Volatility confirmed."
            )

        return result