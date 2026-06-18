const {
  placeOrder
} = require("../services/angelService");

class OrderManager {

  async executeAngelOrder(credentials, orderData) {

    return await placeOrder({
      apiKey: process.env.ANGEL_API_KEY,
      clientId: credentials.clientId,
      password: credentials.password,
      totp: credentials.totp,
      orderData
    });

  }

}

module.exports = new OrderManager();
