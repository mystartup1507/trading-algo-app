from .analyzers.analysis_result import AnalysisResult


class MarketSnapshot:

    def __init__(self):

        # =====================================================
        # Market Information
        # =====================================================

        self.symbol = None
        self.timeframe = None

        # =====================================================
        # EMA
        # =====================================================

        self.ema_fast = None
        self.ema_slow = None

        self.htf_ema_fast = None
        self.htf_ema_slow = None

        # =====================================================
        # RSI
        # =====================================================

        self.rsi = None

        # =====================================================
        # ADX
        # =====================================================

        self.adx = None
        self.plus_di = None
        self.minus_di = None

        self.htf_adx = None
        self.htf_plus_di = None
        self.htf_minus_di = None

        # =====================================================
        # ATR
        # =====================================================

        self.atr = None

        # =====================================================
        # MACD
        # =====================================================

        self.macd = None
        self.macd_signal = None
        self.macd_histogram = None

        # =====================================================
        # SuperTrend
        # =====================================================

        self.supertrend = None
        self.supertrend_signal = None

        # =====================================================
        # Bollinger Bands
        # =====================================================

        self.bb_upper = None
        self.bb_middle = None
        self.bb_lower = None

        self.current_price = None

        # =====================================================
        # Ichimoku
        # =====================================================

        self.tenkan = None
        self.kijun = None
        self.senkou_a = None
        self.senkou_b = None
        self.chikou = None

        # =====================================================
        # Strategy Analysis
        # =====================================================

        self.trend = AnalysisResult()
        self.momentum = AnalysisResult()
        self.volatility = AnalysisResult()
        self.entry = AnalysisResult()

        self.trade_allowed = False

        # =====================================================
        # Final Decision
        # =====================================================

        self.signal = "HOLD"
        self.reason = ""

        # =====================================================
        # Risk Management
        # =====================================================

        self.risk_percent = 0.0
        self.stop_loss = None
        self.take_profit = None
        self.position_size = None