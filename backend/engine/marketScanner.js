
const { getCandleData } = require("../services/angelService");
const marketUniverse = require("../services/marketUniverse");
const config = require("../config/strategyConfig");


class MarketScanner {

  constructor() {

    this.symbols = marketUniverse.load();

  }

getTradingDay() {

  const now = new Date();

  const ist = new Date(
    now.toLocaleString("en-US", {
      timeZone: "Asia/Kolkata"
    })
  );

  const day = ist.getDay();

  const hour = ist.getHours();

  const minute = ist.getMinutes();

  if (
    day === 1 &&
    (
      hour > 15 ||
      (hour === 15 && minute >= 30)
    )
  ) {
    ist.setDate(ist.getDate() - 3);
  }

  else if (day === 6) {
    ist.setDate(ist.getDate() - 1);
  }

  else if (day === 0) {
    ist.setDate(ist.getDate() - 2);
  }

  else if (
  hour < 9 ||
  (hour === 9 && minute < 15)
) {

  ist.setDate(ist.getDate() - 1);

}

else if (
  hour > 15 ||
  (hour === 15 && minute >= 30)
) {

  ist.setDate(ist.getDate() - 1);

}

  return ist;

}

  formatDate(date) {

    const y = date.getFullYear();

    const m = String(
      date.getMonth() + 1
    ).padStart(2, "0");

    const d = String(
      date.getDate()
    ).padStart(2, "0");

    const h = String(
      date.getHours()
    ).padStart(2, "0");

    const min = String(
      date.getMinutes()
    ).padStart(2, "0");

    return `${y}-${m}-${d} ${h}:${min}`;

  }

  async scan(credentials) {

    const markets = [];


    for (const item of this.symbols) {

      const tradingDay = this.getTradingDay();

      const from = new Date(tradingDay);

      from.setHours(
        9,
        15,
        0,
        0
      );

const to = new Date(tradingDay);

to.setHours(
  15,
  30,
  0,
  0
);



      const fromdate =
        this.formatDate(from);

      const todate =
        this.formatDate(to);

      console.log("FROM:", fromdate);
      console.log("TO:", todate);
      console.log("EXCHANGE:", item.exchange);
      console.log("TOKEN:", item.token);
      console.log("SYMBOL:", item.symbol);

      const candles =
        await getCandleData({

          apiKey:
            process.env.ANGEL_API_KEY,

          clientId:
            credentials.clientId,

          password:
            credentials.password,

          totp:
            credentials.totp,

          params: {

            exchange:
              item.exchange,

            symboltoken:
              item.token,

            interval:
              config.timeframe,

            fromdate,

            todate

          }

        });

         await new Promise(resolve => setTimeout(resolve, 300));

        console.log("===== CANDLE RESPONSE =====");
console.log(JSON.stringify(candles, null, 2));

if (
  !candles.success ||
  !candles.data ||
  !candles.data.data ||
  !Array.isArray(candles.data.data)
) {

  console.log("No candle data received.");

  continue;

}


      console.log(
        "Candles received:",
        candles.data.data.length
      );

        console.log(JSON.stringify(candles.data, null, 2));        

        console.log(
  "Last Candle:",
  candles.data.data.at(-1)
);

      markets.push({

        symbol:
          item.symbol,

        token:
          item.token,

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
