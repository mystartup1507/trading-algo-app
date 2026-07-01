const fs = require("fs");
const path = require("path");

class SymbolService {

  constructor() {

    this.masterFile = path.join(
      __dirname,
      "../data/OpenAPIScripMaster.json"
    );

  }

   getAllSymbols() {

  return JSON.parse(
    fs.readFileSync(
      this.masterFile,
      "utf8"
    )
  );

}

  getTradableSymbols() {

    const data = JSON.parse(
      fs.readFileSync(this.masterFile, "utf8")
    );

    return data.filter(item => {

      if (
        item.exch_seg !== "NSE"
      ) {
        return false;
      }

      if (
        item.symbol.endsWith("-EQ")
      ) {
        return true;
      }

      return false;

    });

  }

}

module.exports = new SymbolService();
