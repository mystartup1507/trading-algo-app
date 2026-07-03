const symbolService = require("./symbolService");

class MarketUniverse {

  constructor() {
    this.symbols = [];
  }

  load() {

    const data = symbolService.getAllSymbols();

    const universe = [];
    const added = new Set();

    for (const item of data) {

      if (
        item.exch_seg === "NFO" &&
        (
          item.instrumenttype === "OPTIDX" ||
          item.instrumenttype === "OPTSTK"
        )
      ) {

        if (added.has(item.name)) {
          continue;
        }

        added.add(item.name);

        const equity = data.find(x =>
  x.exch_seg === "NSE" &&
  x.symbol === item.name + "-EQ"
);

if (!equity) {
  continue;
}

const allowed = [
"NIFTY",
"BANKNIFTY",
"RELIANCE",
"HDFCBANK",
"ICICIBANK",
"SBIN",
"TCS",
"INFY",
"LT",
"AXISBANK",
"BAJFINANCE",
"KOTAKBANK",
"ITC",
"HINDUNILVR",
"MARUTI",
"M&M",
"TITAN",
"ULTRACEMCO",
"SUNPHARMA",
"BHARTIARTL",
"NTPC",
"POWERGRID",
"ADANIENT",
"ADANIPORTS",
"TATASTEEL",
"JSWSTEEL",
"HCLTECH",
"WIPRO",
"TECHM",
"INDUSINDBK",
"TATAMOTORS",
"ONGC",
"COALINDIA",
"CIPLA",
"DRREDDY",
"GRASIM",
"EICHERMOT",
"HEROMOTOCO",
"BAJAJFINSV",
"BAJAJ-AUTO",
"NESTLEIND",
"ASIANPAINT",
"SHRIRAMFIN",
"BEL",
"HAL",
"DLF",
"PNB",
"CANBK",
"SAIL",
"IOC"
];

if (!allowed.includes(item.name)) {
    continue;
}

universe.push({
  name: item.name,
  symbol: equity.symbol,
  token: equity.token,
  exchange: "NSE",
  hasOptions: true,
  optionType: item.instrumenttype,
  lotSize: Number(item.lotsize)
});

      }

    }

    universe.sort((a, b) =>
  a.name.localeCompare(b.name)
);

    this.symbols = universe;

    console.log(
      "Universe Loaded:",
      universe.length
    );

    return universe;

  }

  getAll() {
    return this.symbols;
  }

}

module.exports = new MarketUniverse();
