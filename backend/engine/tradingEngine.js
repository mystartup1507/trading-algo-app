const strategyEngine = require("./strategyEngine");
const riskManager = require("./riskManager");
const orderManager = require("./orderManager");
const marketScanner = require("./marketScanner");
const config = require("../config/strategyConfig");

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

if (this.activePositions[marketData.symbol]) {

  console.log(
    `Position already active for ${marketData.symbol}`
  );

  continue;

}

if (
    analysis.signal !== "BUY" ||
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

      const orderData = {

        variety: "NORMAL",

        tradingsymbol: marketData.symbol,

        symboltoken: marketData.token,

        transactiontype: "BUY",

        exchange: "NSE",

        ordertype: "MARKET",

        producttype: "INTRADAY",

        duration: "DAY",

        quantity: 1

      };

      const result =
        await orderManager.executeAngelOrder(
          credentials,
          orderData
        );

      console.log(result);

      if (
  result.success &&
  result.data &&
  result.data.status
) {

  this.activePositions[
    marketData.symbol
  ] = {

    orderId:
      result.data.data.orderid,

    entryTime:
      new Date()

  };

  console.log(
    "Position Saved"
  );

}

    }

  }

}

module.exports = new TradingEngine();
