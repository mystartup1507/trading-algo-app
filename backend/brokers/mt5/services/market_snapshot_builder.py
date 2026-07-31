from indicators import indicator_service
from .market_snapshot import MarketSnapshot
from .analyzers.trend_analyzer import TrendAnalyzer
from .analyzers.momentum_analyzer import MomentumAnalyzer
from .analyzers.volatility_analyzer import VolatilityAnalyzer
from .analyzers.entry_analyzer import EntryAnalyzer


class MarketSnapshotBuilder:

    # ==========================================================
    # HIGHER TIMEFRAME MAPPING
    # ==========================================================
    #
    # Every trading timeframe is confirmed using a genuinely
    # higher timeframe.
    #
    # M1  -> M5
    # M5  -> M15
    # M15 -> H1
    # M30 -> H1
    # H1  -> H4
    # H4  -> D1
    # D1  -> W1
    #
    # ==========================================================

    HIGHER_TIMEFRAME_MAP = {
        "M1": "M5",
        "M5": "M15",
        "M15": "H1",
        "M30": "H1",
        "H1": "H4",
        "H4": "D1",
        "D1": "W1",
    }

    DEFAULT_HIGHER_TIMEFRAME = "H1"

    def __init__(self):

        self.trend_analyzer = TrendAnalyzer()
        self.momentum_analyzer = MomentumAnalyzer()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.entry_analyzer = EntryAnalyzer()

    # ==========================================================
    # HIGHER TIMEFRAME RESOLVER
    # ==========================================================

    def get_higher_timeframe(self, timeframe):

        normalized_timeframe = str(timeframe).upper()

        return self.HIGHER_TIMEFRAME_MAP.get(
            normalized_timeframe,
            self.DEFAULT_HIGHER_TIMEFRAME
        )

    # ==========================================================
    # BUILD MARKET SNAPSHOT
    # ==========================================================

    def build(self, symbol, timeframe):

        snapshot = MarketSnapshot()

        symbol = str(symbol)
        timeframe = str(timeframe).upper()

        snapshot.symbol = symbol
        snapshot.timeframe = timeframe

        higher_timeframe = self.get_higher_timeframe(
            timeframe
        )

        # ======================================================
        # EMA 20 — CURRENT TIMEFRAME
        # ======================================================

        ema20 = indicator_service.ema(
            symbol,
            timeframe,
            20
        )

        if ema20.get("success"):
            snapshot.ema_fast = (
                ema20["data"]["ema"]
            )

        # ======================================================
        # EMA 50 — CURRENT TIMEFRAME
        # ======================================================

        ema50 = indicator_service.ema(
            symbol,
            timeframe,
            50
        )

        if ema50.get("success"):
            snapshot.ema_slow = (
                ema50["data"]["ema"]
            )

        # ======================================================
        # EMA 20 — HIGHER TIMEFRAME
        # ======================================================

        htf_ema20 = indicator_service.ema(
            symbol,
            higher_timeframe,
            20
        )

        if htf_ema20.get("success"):
            snapshot.htf_ema_fast = (
                htf_ema20["data"]["ema"]
            )

        # ======================================================
        # EMA 50 — HIGHER TIMEFRAME
        # ======================================================

        htf_ema50 = indicator_service.ema(
            symbol,
            higher_timeframe,
            50
        )

        if htf_ema50.get("success"):
            snapshot.htf_ema_slow = (
                htf_ema50["data"]["ema"]
            )

        # ======================================================
        # RSI — CURRENT TIMEFRAME
        # ======================================================

        rsi = indicator_service.rsi(
            symbol,
            timeframe,
            14
        )

        if rsi.get("success"):
            snapshot.rsi = (
                rsi["data"]["rsi"]
            )

        # ======================================================
        # ADX — CURRENT TIMEFRAME
        # ======================================================

        adx = indicator_service.adx(
            symbol,
            timeframe,
            14
        )

        if adx.get("success"):

            snapshot.adx = (
                adx["data"]["adx"]
            )

            snapshot.plus_di = (
                adx["data"]["+di"]
            )

            snapshot.minus_di = (
                adx["data"]["-di"]
            )

        # ======================================================
        # ADX — HIGHER TIMEFRAME
        # ======================================================

        htf_adx = indicator_service.adx(
            symbol,
            higher_timeframe,
            14
        )

        if htf_adx.get("success"):

            snapshot.htf_adx = (
                htf_adx["data"]["adx"]
            )

            snapshot.htf_plus_di = (
                htf_adx["data"]["+di"]
            )

            snapshot.htf_minus_di = (
                htf_adx["data"]["-di"]
            )

        # ======================================================
        # ATR — CURRENT TIMEFRAME
        # ======================================================

        atr = indicator_service.atr(
            symbol,
            timeframe,
            14
        )

        if atr.get("success"):
            snapshot.atr = (
                atr["data"]["atr"]
            )

        # ======================================================
        # MACD — CURRENT TIMEFRAME
        # ======================================================

        macd = indicator_service.macd(
            symbol,
            timeframe
        )

        if macd.get("success"):

            snapshot.macd = (
                macd["data"]["macd"]
            )

            snapshot.macd_signal = (
                macd["data"]["signal"]
            )

            snapshot.macd_histogram = (
                macd["data"]["histogram"]
            )

        # ======================================================
        # MARKET ANALYSIS
        # ======================================================

        snapshot.trend = (
            self.trend_analyzer.analyze(
                snapshot
            )
        )

        snapshot.momentum = (
            self.momentum_analyzer.analyze(
                snapshot
            )
        )

        snapshot.volatility = (
            self.volatility_analyzer.analyze(
                snapshot
            )
        )

        snapshot.entry = (
            self.entry_analyzer.analyze(
                snapshot
            )
        )

        return snapshot


market_snapshot_builder = MarketSnapshotBuilder()