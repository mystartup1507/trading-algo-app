const { getMarketData } = require("./angelService");

class LTPService {

  async getLTP(credentials, exchange, tradingsymbol, symboltoken) {

    const result = await getMarketData({

      apiKey: process.env.ANGEL_API_KEY,

      clientId: credentials.clientId,

      password: credentials.password,

      totp: credentials.totp,

      mode: "LTP",

      exchange,

      symboltoken

    });

    if (!result.success) {

      console.log(result);

      return {
        success: false
      };

    }

    const quote =
      result.data.data.fetched[0];

    return {

      success: true,

      price: Number(quote.ltp)

    };

  }

}

module.exports = new LTPService();
