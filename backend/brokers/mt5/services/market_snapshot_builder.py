from indicators import indicator_service
from .market_snapshot import MarketSnapshot
from .analyzers.trend_analyzer import TrendAnalyzer
from .analyzers.momentum_analyzer import MomentumAnalyzer
from .analyzers.volatility_analyzer import VolatilityAnalyzer
from .analyzers.entry_analyzer import EntryAnalyzer


class MarketSnapshotBuilder:

    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.momentum_analyzer = MomentumAnalyzer()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.entry_analyzer = EntryAnalyzer()

    def build(self, symbol, timeframe):

        snapshot = MarketSnapshot()

        snapshot.symbol = symbol
        snapshot.timeframe = timeframe

        #
        # EMA
        #
     #
# EMA 20
#
        ema20 = indicator_service.ema(
            symbol,
            timeframe,
            20
        )

        if ema20["success"]:
            snapshot.ema_fast = ema20["data"]["ema"]


#
# EMA 50
#
        ema50 = indicator_service.ema(
            symbol,
            timeframe,
            50
        )

        if ema50["success"]:
            snapshot.ema_slow = ema50["data"]["ema"]

        #
# Higher Timeframe EMA20 (M15)
#
        htf_ema20 = indicator_service.ema(
            symbol,
            "M15",
            20
        )

        if htf_ema20["success"]:
            snapshot.htf_ema_fast = htf_ema20["data"]["ema"]


#
# Higher Timeframe EMA50 (M15)
#
        htf_ema50 = indicator_service.ema(
            symbol,
            "M15",
            50
        )

        if htf_ema50["success"]:
            snapshot.htf_ema_slow = htf_ema50["data"]["ema"]

        #
        # RSI
        #
        rsi = indicator_service.rsi(
            symbol,
            timeframe,
            14
        )

        if rsi["success"]:
            snapshot.rsi = rsi["data"]["rsi"]

        #
        # ADX
        #
        adx = indicator_service.adx(
            symbol,
            timeframe
        )

        print(adx)

        if adx["success"]:
            snapshot.adx = adx["data"]["adx"]
            snapshot.plus_di = adx["data"]["+di"]
            snapshot.minus_di = adx["data"]["-di"]

        #
# Higher Timeframe ADX (M15)
#
        htf_adx = indicator_service.adx(
            symbol,
            "M15"
        )

        if htf_adx["success"]:
            snapshot.htf_adx = htf_adx["data"]["adx"]
            snapshot.htf_plus_di = htf_adx["data"]["+di"]
            snapshot.htf_minus_di = htf_adx["data"]["-di"]

        #
        # ATR
        #
        atr = indicator_service.atr(
            symbol,
            timeframe,
            14
        )

        if atr["success"]:
            snapshot.atr = atr["data"]["atr"]

        #
        # MACD
        #
        macd = indicator_service.macd(
            symbol,
            timeframe
        )

        if macd["success"]:
            snapshot.macd = macd["data"]["macd"]
            snapshot.macd_signal = macd["data"]["signal"]
            snapshot.macd_histogram = macd["data"]["histogram"]


        snapshot.trend = self.trend_analyzer.analyze(snapshot)
        snapshot.momentum = self.momentum_analyzer.analyze(snapshot)
        snapshot.volatility = self.volatility_analyzer.analyze(snapshot)
        snapshot.entry = self.entry_analyzer.analyze(snapshot)

        return snapshot


market_snapshot_builder = MarketSnapshotBuilder()