from .analyzers.analysis_result import AnalysisResult


class MarketSnapshot:

    def __init__(self):

        # ===========================
        # Market Information
        # ===========================

        self.symbol = None
        self.timeframe = None

        # ===========================
        # Indicator Values
        # ===========================

        #
# Current Timeframe EMA
#
        self.ema_fast = None
        self.ema_slow = None

#
# Higher Timeframe EMA
#
        self.htf_ema_fast = None
        self.htf_ema_slow = None

        self.rsi = None

        self.adx = None
        self.plus_di = None
        self.minus_di = None

        self.atr = None

        self.macd = None
        self.macd_signal = None
        self.macd_histogram = None

        self.htf_adx = None
        self.htf_plus_di = None
        self.htf_minus_di = None

        # ===========================
        # Strategy Analysis
        # ===========================

        self.trend = AnalysisResult()

        self.momentum = AnalysisResult()

        self.volatility = AnalysisResult()

        self.entry = AnalysisResult()

        self.trade_allowed = False

        # ===========================
        # Final Decision
        # ===========================

        self.signal = "HOLD"

        self.reason = ""

        # ===========================
        # Risk Information
        # ===========================

        self.risk_percent = 0.0

        self.stop_loss = None

        self.take_profit = None

        self.position_size = None