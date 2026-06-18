const strategyEngine = require("./strategyEngine");
const riskManager = require("./riskManager");
const orderManager = require("./orderManager");
const marketScanner = require("./marketScanner");

class TradingEngine {

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

      if (analysis.signal !== "BUY") {
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

    }

  }

}

module.exports = new TradingEngine();
