const strategyEngine = require("./strategyEngine");
const riskManager = require("./riskManager");
const orderManager = require("./orderManager");
const marketScanner = require("./marketScanner");
const config = require("../config/strategyConfig");
const optionSelector = require("../services/optionSelector");
const {
    getLTPData
} = require("../services/angelService");
const positionManager = require("./positionManager");

class TradingEngine {
  constructor() {

    this.activePositions = {};

  }


  async start(credentials, account) {

    console.log("===== JD-Algo Started =====");

    const market =
      await marketScanner.scan(credentials);

    if (!market.success) {
      return;
    }

    for (const marketData of market.markets) {

      console.log(`Scanning ${marketData.symbol}...`);

      const analysis =
        strategyEngine.analyze(
          marketData.candles
        );

      console.log(analysis);

if (
  Object.keys(this.activePositions).length > 0
) {

  console.log(
    "Active position exists. Skipping new trades."
  );

  continue;

}

if (
    analysis.signal === "WAIT" ||
    analysis.confidence < config.ai.confidenceThreshold
) {

    console.log("Trade Skipped");

    continue;

}

      const risk =
        riskManager.validateTrade(
          account,
          analysis
        );

      if (!risk.allowed) {

        console.log(risk.reason);
        continue;

      }

      const stockPrice =
    marketData.candles[
        marketData.candles.length - 1
    ][4];

const stockSymbol =
    marketData.symbol.replace("-EQ", "");

const indexName =
    optionSelector.getIndexForStock(stockSymbol);

const indexToken =
    optionSelector.getIndexToken(indexName);

const ltp =
    await getLTPData({

        apiKey: process.env.ANGEL_API_KEY,

        clientId: credentials.clientId,

        password: credentials.password,

        totp: credentials.totp,

        params: {
            exchange: "NSE",
            tradingsymbol: indexName,
            symboltoken: indexToken
        }

    });

if (
    !ltp.success ||
    !ltp.data ||
    !ltp.data.data
) {

    console.log("Unable to fetch Index LTP");

    continue;

}

const entryPrice =
    Number(
        ltp.data.data.fetched[0].ltp
    );

console.log("INDEX LTP :", entryPrice);

const option =
    optionSelector.getATMOption(
        stockSymbol,
        analysis.signal,
        entryPrice
    );

if (!option) {

    console.log("No suitable option found");
    continue;

}

console.log("Selected Option:");
console.log(option);

const stopLoss =
  Number(
    (
      entryPrice -
      analysis.indicators.atr * 2
    ).toFixed(2)
  );

const target =
  Number(
    (
      entryPrice +
      (entryPrice - stopLoss) * 2
    ).toFixed(2)
  );

console.log("ENTRY :", entryPrice);
console.log("SL    :", stopLoss);
console.log("TARGET:", target);
       
       const orderData = {

  variety: "NORMAL",

  tradingsymbol: option.symbol,

  symboltoken: option.token,

  transactiontype:
    analysis.signal === "SELL"
      ? "BUY"
      : "BUY",

  exchange: "NFO",

  ordertype: "MARKET",

  producttype: "INTRADAY",

  duration: "DAY",

  quantity: Number(option.lotsize)

};

      const result =
        await orderManager.executeAngelOrder(
          credentials,
          orderData
        );

       if (
  result.success &&
  result.data &&
  result.data.status
) {

  console.log("===============");
  console.log("TRADE DETAILS");
  console.log("Entry :", entryPrice);
  console.log("SL    :", stopLoss);
  console.log("Target:", target);
  console.log("===============");

}

      console.log(result);

if (
  result.success &&
  result.data &&
  result.data.status
) {

  const orderStatus =
    await orderManager.waitForOrderCompletion(
      credentials,
      result.data.data.orderid
    );

  console.log(orderStatus);

  if (!orderStatus.success) {

    console.log("Order was not completed.");

    continue;

  }

this.activePositions[
  marketData.symbol
] = {

  credentials,

  symbol: marketData.symbol,

  option: option.symbol,

  optionToken: option.token,

  exchange: "NFO",

  orderId: orderStatus.order.orderid,

  entry: entryPrice,

  sl: stopLoss,

  target: target,

  quantity: Number(option.lotsize),

  entryTime: new Date(),
  orderStatus: "COMPLETE"

};

  console.log(
    "Position Saved"
  );

}

    }

      await positionManager.monitor(
      this.activePositions
    );

  }

}

module.exports = new TradingEngine();
