const {
  placeOrder,
  getPositions,
  getOrderBook
} = require("../services/angelService");

class OrderManager {

  async executeAngelOrder(credentials, orderData) {

    console.log("===== ORDER MANAGER =====");
    console.log({
      clientId: credentials.clientId,
      hasPassword: !!credentials.password,
      hasTotp: !!credentials.totp
    });

    return await placeOrder({
      apiKey: process.env.ANGEL_API_KEY,
      clientId: credentials.clientId,
      password: credentials.password,
      totp: credentials.totp,
      orderData
    });

  }

  async getOpenPositions(credentials) {

    return await getPositions({
      apiKey: process.env.ANGEL_API_KEY,
      clientId: credentials.clientId,
      password: credentials.password,
      totp: credentials.totp
    });

  }

async waitForOrderCompletion(credentials, orderId) {

    console.log("WAITING FOR ORDER :", orderId);

    for (let i = 0; i < 10; i++) {

        const book = await getOrderBook({
            apiKey: process.env.ANGEL_API_KEY,
            clientId: credentials.clientId,
            password: credentials.password,
            totp: credentials.totp
        });

        if (!book.success) {

            console.log("ORDER BOOK ERROR :", book.message);

            await new Promise(r => setTimeout(r, 5000));

            continue;
        }

         if (
    !book.data ||
    !book.data.data ||
    !Array.isArray(book.data.data)
) {

    console.log("===== INVALID ORDER BOOK =====");
    console.log(JSON.stringify(book, null, 2));

    await new Promise(r => setTimeout(r, 5000));

    continue;
}

        const order = book.data.data.find(
            o => o.orderid === orderId
        );

        if (!order) {

            console.log("ORDER NOT FOUND");

            await new Promise(r => setTimeout(r, 3000));

            continue;
        }

        console.log("ORDER STATUS :", order.orderstatus);

        if (order.orderstatus === "complete") {

            return {
                success: true,
                order
            };

        }

        if (
            ["cancelled", "rejected", "failed"].includes(
                order.orderstatus.toLowerCase()
            )
        ) {

            return {
                success: false,
                order
            };

        }

        await new Promise(r => setTimeout(r, 3000));
    }

    return {
        success: false,
        timeout: true
    };
}

}

module.exports = new OrderManager();
