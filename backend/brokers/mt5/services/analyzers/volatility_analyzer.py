from .analysis_result import AnalysisResult


class VolatilityAnalyzer:

    def analyze(self, snapshot):

        result = AnalysisResult()

        if snapshot.atr is None:
            result.reason = "ATR unavailable."
            return result

        atr = snapshot.atr

        if atr < 0.00015:
            result.state = "LOW"
            result.score = 20
            result.confidence = 0.90
            result.reason = "Low volatility."

        elif atr < 0.00035:
            result.state = "NORMAL"
            result.score = 80
            result.confidence = 0.95
            result.reason = "Normal volatility."

        else:
            result.state = "HIGH"
            result.score = 50
            result.confidence = 0.80
            result.reason = "High volatility."

        return result