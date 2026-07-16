from flask import Flask, jsonify, request
from account import account_service
from market import market_service
from indicators import indicator_service


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

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
