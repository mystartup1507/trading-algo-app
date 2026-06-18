const { getCandleData } = require("../services/angelService");
const config = require("../config/strategyConfig");

class MarketScanner {

  constructor() {

    this.symbols = [

      {
        symbol: "SBIN-EQ",
        token: "3045",
        exchange: "NSE"
      }

    ];

  }

  async scan(credentials) {

    const markets = [];

    for (const item of this.symbols) {

      const now = new Date();

      const todate = now
        .toISOString()
        .slice(0, 16)
        .replace("T", " ");

      const from = new Date(
        now.getTime() - 100 * 5 * 60 * 1000
      );

      const fromdate = from
        .toISOString()
        .slice(0, 16)
        .replace("T", " ");

      const candles = await getCandleData({

        apiKey: process.env.ANGEL_API_KEY,

        clientId: credentials.clientId,

        password: credentials.password,

        totp: credentials.totp,

        params: {

          exchange: item.exchange,

          symboltoken: item.token,

          interval: config.timeframe,

          fromdate,

          todate

        }

      });

      if (!candles.success)
        continue;

      markets.push({

        symbol: item.symbol,

        token: item.token,

        candles:
          candles.data.data

      });

    }

    return {

      success: true,

      markets

    };

  }

}

module.exports = new MarketScanner();
