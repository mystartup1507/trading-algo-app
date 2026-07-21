from flask import Flask, jsonify, request
from account import account_service
from market import market_service
from indicators import indicator_service
from trading_engine import trading_engine
from services.market_snapshot_builder import market_snapshot_builder

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "message": "MT5 Bridge Running"
    })

@app.route("/account")
def account():

    result = account_service.get_account_info()

    return jsonify(result)



@app.route("/symbols")
def symbols():

    result = market_service.get_symbols()

    return jsonify(result)


@app.route("/tick/<symbol>")
def tick(symbol):

    result = market_service.get_tick(symbol.upper())

    return jsonify(result)

@app.route("/candles/<symbol>/<timeframe>/<int:count>")
def candles(symbol, timeframe, count):

    result = market_service.get_candles(
        symbol.upper(),
        timeframe.upper(),
        count
    )

    return jsonify(result)

@app.route("/indicator/ema/<symbol>/<timeframe>/<int:period>")
def ema(symbol, timeframe, period):

    result = indicator_service.ema(
        symbol.upper(),
        timeframe.upper(),
        period
    )

    return jsonify(result)

@app.route("/indicator/rsi/<symbol>/<timeframe>/<int:period>")
def rsi(symbol, timeframe, period):

    result = indicator_service.rsi(
        symbol.upper(),
        timeframe.upper(),
        period
    )

    return jsonify(result)

@app.route("/indicator/atr/<symbol>/<timeframe>/<int:period>")
def atr(symbol, timeframe, period):

    result = indicator_service.atr(
        symbol,
        timeframe,
        period
    )

    return jsonify(result)

@app.route("/indicator/supertrend/<symbol>/<timeframe>/<int:period>/<int:multiplier>")
def supertrend(symbol, timeframe, period, multiplier):

    result = indicator_service.supertrend(
        symbol,
        timeframe,
        period,
        multiplier
    )

    return jsonify(result)

@app.route(
    "/indicator/macd/<symbol>/<timeframe>",
    methods=["GET"]
)
def macd(symbol, timeframe):

    result = indicator_service.macd(
        symbol.upper(),
        timeframe.upper()
    )

    return jsonify(result)

@app.route(
    "/indicator/adx/<symbol>/<timeframe>/<int:period>",
    methods=["GET"]
)
def adx(symbol, timeframe, period):

    result = indicator_service.adx(
        symbol.upper(),
        timeframe.upper(),
        period
    )

    return jsonify(result)


@app.route(
    "/signal/<symbol>/<timeframe>",
    methods=["GET"]
)
def signal(symbol, timeframe):

    result = trading_engine.generate_signal(
        symbol.upper(),
        timeframe.upper()
    )

    return jsonify(result)

@app.route(
    "/snapshot/<symbol>/<timeframe>",
    methods=["GET"]
)
def snapshot(symbol, timeframe):

    snapshot = market_snapshot_builder.build(
        symbol.upper(),
        timeframe.upper()
    )

    return jsonify({
        "symbol": snapshot.symbol,
        "timeframe": snapshot.timeframe,
        "ema_fast": snapshot.ema_fast,
        "ema_slow": snapshot.ema_slow,
        "htf_ema_fast": snapshot.htf_ema_fast,
        "htf_ema_slow": snapshot.htf_ema_slow,
        "rsi": snapshot.rsi,
        "adx": snapshot.adx,
        "plus_di": snapshot.plus_di,
        "minus_di": snapshot.minus_di,
        "htf_adx": snapshot.htf_adx,
        "htf_plus_di": snapshot.htf_plus_di,
        "htf_minus_di": snapshot.htf_minus_di,
        "atr": snapshot.atr,
        "macd": snapshot.macd,
        "macd_signal": snapshot.macd_signal,
        "macd_histogram": snapshot.macd_histogram,
        "trend": {
            "state": snapshot.trend.state,
            "score": snapshot.trend.score,
            "confidence": snapshot.trend.confidence,
            "reason": snapshot.trend.reason
        },
        "momentum": {
            "state": snapshot.momentum.state,
            "score": snapshot.momentum.score,
            "confidence": snapshot.momentum.confidence,
            "reason": snapshot.momentum.reason
        },
        "volatility": {
            "state": snapshot.volatility.state,
            "score": snapshot.volatility.score,
            "confidence": snapshot.volatility.confidence,
            "reason": snapshot.volatility.reason
        },
           
    })
@app.route("/symbol/<symbol>", methods=["GET"])
def get_symbol_info(symbol):

    result = indicator_service.symbol_info(symbol)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/account", methods=["GET"])
def get_account_info():

    result = indicator_service.account_info()

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/positions", methods=["GET"])
def get_positions():

    result = indicator_service.positions()

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
