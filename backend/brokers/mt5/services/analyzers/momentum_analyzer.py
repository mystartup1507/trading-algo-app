from .analysis_result import AnalysisResult


class MomentumAnalyzer:

    def analyze(self, snapshot):

        result = AnalysisResult()

        if (
            snapshot.rsi is None or
            snapshot.macd is None or
            snapshot.macd_signal is None or
            snapshot.adx is None
        ):
            result.reason = "Momentum data unavailable."
            return result

        score = 0

        if snapshot.rsi > 55:
            score += 1

        if snapshot.macd > snapshot.macd_signal:
            score += 1

        if snapshot.adx > 20:
            score += 1

        if score == 3:
            result.state = "STRONG"
            result.score = 100
            result.confidence = 0.95
            result.reason = "Strong bullish momentum."

        elif score == 2:
            result.state = "MODERATE"
            result.score = 70
            result.confidence = 0.75
            result.reason = "Moderate momentum."

        else:
            result.state = "WEAK"
            result.score = 30
            result.confidence = 0.60
            result.reason = "Weak momentum."

        return result