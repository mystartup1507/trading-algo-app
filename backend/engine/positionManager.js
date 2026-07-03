const ltpService = require("../services/ltpService");
const orderManager =
require("./orderManager");

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

const result = await orderManager.executeAngelOrder(
    position.credentials,
    {
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
);

console.log(result);

if (
    result.success &&
    result.data &&
    result.data.status
) {

    const exitStatus =
        await orderManager.waitForOrderCompletion(
            position.credentials,
            result.data.data.orderid
        );

    console.log("===== EXIT ORDER STATUS =====");
    console.log(JSON.stringify(exitStatus, null, 2));

    if (exitStatus.success) {

        delete activePositions[symbol];

        console.log("Position Closed");

    } else {

        console.log("Exit order not completed.");

    }

}


}

        }

    }

}

module.exports = new PositionManager();
