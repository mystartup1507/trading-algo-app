from flask import Flask, jsonify, request
from account import account_service
from market import market_service
from indicators import indicator_service
from trading_engine import trading_engine
from services.market_snapshot_builder import market_snapshot_builder
from strategies.strategy_manager import StrategyManager
from decision.decision_engine import decision_engine
from risk.risk_engine import risk_engine

app = Flask(__name__)

strategy_manager = StrategyManager()

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

@app.route("/bollinger-bands", methods=["GET"])
def bollinger_bands():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe")
    
    print("SYMBOL:", symbol)
    print("TIMEFRAME:", timeframe)    

    period = int(request.args.get("period", 20))
    deviation = float(request.args.get("deviation", 2))

    result = indicator_service.bollinger_bands(
        symbol,
        timeframe,
        period,
        deviation
    )

    return jsonify(result)

@app.route("/vwap", methods=["GET"])
def vwap():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    result = indicator_service.vwap(
        symbol,
        timeframe
    )

    return jsonify(result)

@app.route("/ichimoku", methods=["GET"])
def ichimoku():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    result = indicator_service.ichimoku(
        symbol,
        timeframe
    )

    return jsonify(result)

@app.route("/decision", methods=["GET"])
def decision():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    result = decision_engine.analyze(
        symbol,
        timeframe
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

@app.route("/strategy/ema-crossover", methods=["GET"])
def ema_crossover_strategy():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    strategy = strategy_manager.get_strategy("ema_crossover")

    result = strategy.generate_signal(
        symbol,
        timeframe
    )

    return jsonify(result)

@app.route("/strategy/macd", methods=["GET"])
def macd_strategy():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    strategy = strategy_manager.get_strategy("macd")

    result = strategy.generate_signal(
        symbol,
        timeframe
    )

    return jsonify(result)

@app.route("/strategy/supertrend", methods=["GET"])
def supertrend_strategy():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    period = int(request.args.get("period", 10))
    multiplier = int(request.args.get("multiplier", 3))

    strategy = strategy_manager.get_strategy("supertrend")

    result = strategy.generate_signal(
        symbol,
        timeframe,
        period,
        multiplier
    )

    return jsonify(result)

@app.route("/strategy/bollinger", methods=["GET"])
def bollinger_strategy():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    period = int(request.args.get("period", 20))
    deviation = float(request.args.get("deviation", 2))

    strategy = strategy_manager.get_strategy("bollinger")

    result = strategy.generate_signal(
        symbol,
        timeframe,
        period,
        deviation
    )

    return jsonify(result)

@app.route("/strategy/ichimoku", methods=["GET"])
def ichimoku_strategy():

    symbol = request.args.get("symbol")
    timeframe = request.args.get("timeframe", "").upper().strip()

    strategy = strategy_manager.get_strategy("ichimoku")

    result = strategy.generate_signal(
        symbol,
        timeframe
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

@app.route("/market-order", methods=["POST"])
def market_order():

    data = request.get_json()

    result = indicator_service.market_order(
        symbol=data["symbol"],
        volume=data["volume"],
        order_type=data["order_type"],
        sl=data.get("sl", 0.0),
        tp=data.get("tp", 0.0),
        comment=data.get("comment", "JD-Algo"),
        magic=data.get("magic", 1001)
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/close-position", methods=["POST"])
def close_position():

    data = request.get_json()

    result = indicator_service.close_position(
        ticket=data["ticket"]
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/modify-position", methods=["POST"])
def modify_position():

    data = request.get_json()

    result = indicator_service.modify_position(
        ticket=data["ticket"],
        sl=data.get("sl"),
        tp=data.get("tp")
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/pending-order", methods=["POST"])
def pending_order():

    data = request.get_json()

    result = indicator_service.pending_order(
        symbol=data["symbol"],
        volume=data["volume"],
        order_type=data["order_type"],
        price=data["price"],
        sl=data.get("sl", 0.0),
        tp=data.get("tp", 0.0),
        comment=data.get("comment", "JD-Algo Pending"),
        magic=data.get("magic", 1001)
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/pending-orders", methods=["GET"])
def get_pending_orders():

    result = indicator_service.get_pending_orders()

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/pending-order/<int:ticket>", methods=["GET"])
def get_pending_order(ticket):

    result = indicator_service.get_pending_order(ticket)

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/modify-pending-order", methods=["POST"])
def modify_pending_order():

    data = request.get_json()

    result = indicator_service.modify_pending_order(
        ticket=data["ticket"],
        price=data["price"],
        sl=data.get("sl"),
        tp=data.get("tp")
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/cancel-pending-order", methods=["POST"])
def cancel_pending_order():

    data = request.get_json()

    result = indicator_service.cancel_pending_order(
        ticket=data["ticket"]
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/close-positions-by-symbol", methods=["POST"])
def close_positions_by_symbol():

    data = request.get_json()

    result = indicator_service.close_positions_by_symbol(
        symbol=data["symbol"]
    )

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/close-all-positions", methods=["POST"])
def close_all_positions():

    result = indicator_service.close_all_positions()

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/order-history", methods=["GET"])
def order_history():

    result = indicator_service.order_history()

    if not result["success"]:
        return jsonify(result), 400

    return jsonify(result)

@app.route("/risk", methods=["GET"])
def risk():

    risk_percent = request.args.get("risk_percent")

    if risk_percent is not None:
        risk_percent = float(risk_percent)

    result = risk_engine.calculate_risk(risk_percent)

    return jsonify(result)

@app.route("/lot-size", methods=["GET"])
def lot_size():

    symbol = request.args.get("symbol")

    risk_percent = float(
        request.args.get("risk_percent", 2)
    )

    stop_loss_pips = float(
        request.args.get("stop_loss_pips")
    )

    result = risk_engine.calculate_lot_size(
        symbol,
        risk_percent,
        stop_loss_pips
    )

    return jsonify(result)

@app.route("/stop-loss", methods=["GET"])
def stop_loss():

    symbol = request.args.get("symbol")

    timeframe = request.args.get("timeframe")

    direction = request.args.get("direction")

    multiplier = request.args.get("multiplier")

    if multiplier is not None:
        multiplier = float(multiplier)

    result = risk_engine.calculate_stop_loss(
        symbol,
        timeframe,
        direction,
        multiplier
    )

    return jsonify(result)

@app.route("/take-profit", methods=["GET"])
def take_profit():

    entry_price = float(
        request.args.get("entry_price")
    )

    stop_loss = float(
        request.args.get("stop_loss")
    )

    direction = request.args.get("direction")

    risk_reward = request.args.get("risk_reward")

    if risk_reward is not None:
        risk_reward = float(risk_reward)

    result = risk_engine.calculate_take_profit(
        entry_price,
        stop_loss,
        direction,
        risk_reward
    )

    return jsonify(result)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
