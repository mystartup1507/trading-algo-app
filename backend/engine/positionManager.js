const ltpService = require("../services/ltpService");
const { placeOrder } = require("../services/angelService");

class PositionManager {

    async monitor(activePositions) {

        const positions = Object.keys(activePositions);

        if (!positions.length) return;

        for (const symbol of positions) {

            const position = activePositions[symbol];

            const ltp = await ltpService.getLTP(
                position.credentials,
                position.exchange,
                position.option,
                position.optionToken
            );

            if (!ltp.success) {

                console.log("Unable to fetch LTP");
                continue;

            }

            const price = Number(ltp.price);

            console.log(
                `${position.option} : ${price}`
            );


             if (price <= position.sl || price >= position.target) {

    console.log(
        price <= position.sl
            ? "STOP LOSS HIT"
            : "TARGET HIT"
    );

    const result = await placeOrder({

        apiKey: process.env.ANGEL_API_KEY,

        clientId: position.credentials.clientId,

        password: position.credentials.password,

        totp: position.credentials.totp,

        orderData: {

            variety: "NORMAL",

            tradingsymbol: position.option,

            symboltoken: position.optionToken,

            transactiontype: "SELL",

            exchange: "NFO",

            ordertype: "MARKET",

            producttype: "INTRADAY",

            duration: "DAY",

            quantity: position.quantity

        }

    });

    console.log(result);

    if (result.success) {

        delete activePositions[symbol];

        console.log("Position Closed");

    }

}

        }

    }

}

module.exports = new PositionManager();
