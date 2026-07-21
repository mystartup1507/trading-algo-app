from .analysis_result import AnalysisResult


class TrendAnalyzer:

    def analyze(self, snapshot):

        result = AnalysisResult()

        if (
            snapshot.htf_ema_fast is None 
            or snapshot.htf_ema_slow is None
        ):
            result.reason = "EMA data unavailable."
            return result

        if snapshot.htf_adx is None:
            result.reason = "ADX data unavailable."
            return result

        if snapshot.htf_adx < 15:
            result.state = "SIDEWAYS"
            result.score = 50
            result.confidence = 0.90
            result.reason = "ADX below 15."
            return result

        if snapshot.htf_ema_fast > snapshot.htf_ema_slow:

            if snapshot.htf_adx >= 25:
                result.state = "UPTREND"
                result.score = 90
                result.confidence = 0.95
                result.reason = "Strong bullish trend."

            else:
                result.state = "WEAK_UPTREND"
                result.score = 70
                result.confidence = 0.75
                result.reason = "Weak bullish trend."

        else:

            if snapshot.htf_adx >= 25:
                result.state = "DOWNTREND"
                result.score = 10
                result.confidence = 0.95
                result.reason = "Strong bearish trend."

            else:
                result.state = "WEAK_DOWNTREND"
                result.score = 30
                result.confidence = 0.75
                result.reason = "Weak bearish trend."

        return result