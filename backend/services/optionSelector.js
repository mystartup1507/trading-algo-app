const symbolService = require("./symbolService");

class OptionSelector {

  constructor() {
    this.data = symbolService.getAllSymbols();
  }

getStrikePrice(price, index) {

    switch (index) {

        case "BANKNIFTY":
            return Math.round(price / 100) * 100;

        case "FINNIFTY":
            return Math.round(price / 50) * 50;

        case "MIDCPNIFTY":
            return Math.round(price / 25) * 25;

        default: // NIFTY
            return Math.round(price / 50) * 50;

    }

}

   getIndexForStock(symbol) {

    const bankStocks = [
        "HDFCBANK",
        "ICICIBANK",
        "AXISBANK",
        "KOTAKBANK",
        "SBIN",
        "BANKBARODA",
        "PNB",
        "CANBK",
        "INDUSINDBK",
        "FEDERALBNK",
        "AUBANK",
        "IDFCFIRSTB"
    ];

    const financeStocks = [
        "BAJFINANCE",
        "BAJAJFINSV",
        "JIOFIN",
        "CHOLAFIN",
        "SHRIRAMFIN",
        "MUTHOOTFIN",
        "LICHSGFIN",
        "PFC",
        "RECLTD",
        "SBICARD"
    ];

    if (bankStocks.includes(symbol))
        return "BANKNIFTY";

    if (financeStocks.includes(symbol))
        return "FINNIFTY";

    return "NIFTY";
}  

getIndexToken(index) {

    switch (index) {

        case "NIFTY":
            return "99926000";

        case "BANKNIFTY":
            return "99926009";

        case "FINNIFTY":
            return "99926037";

        case "MIDCPNIFTY":
            return "99926074";

        default:
            return "99926000";

    }

}

getATMOption(symbol, direction, price) {

    const index = this.getIndexForStock(symbol);

    const strike = this.getStrikePrice(price, index);

    console.log({
    stock: symbol,
    index,
    strike,
    price
}); 

    const options = this.data.filter(item => {

        if (item.exch_seg !== "NFO")
            return false;

        if (item.instrumenttype !== "OPTIDX")
            return false;

        if (item.name !== index)
            return false;

        item.optionStrike = Number(item.strike) / 100;

        if (direction === "BUY")
            return item.symbol.endsWith("CE");

        if (direction === "SELL")
            return item.symbol.endsWith("PE");

        return false;

    });

const today = new Date();

const validOptions = options.filter(item => {
    const expiry = new Date(item.expiry);

    expiry.setHours(23,59,59,999);

    return expiry >= today;
});

validOptions.sort((a, b) => {

    const expiryDiff =
        new Date(a.expiry) - new Date(b.expiry);

    if (expiryDiff !== 0)
        return expiryDiff;

    return (
        Math.abs(a.optionStrike - strike) -
        Math.abs(b.optionStrike - strike)
    );

});

return validOptions[0] || null;

}


}

module.exports = new OptionSelector();
