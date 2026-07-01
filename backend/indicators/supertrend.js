const calculateATR = require("./atr");

function calculateSupertrend(candles, multiplier = 3) {

    const atr = calculateATR(candles);

    if (!atr.length)
        return [];

    const trend = [];

    for (let i = 14; i < candles.length; i++) {

        const high = Number(candles[i][2]);
        const low = Number(candles[i][3]);
        const close = Number(candles[i][4]);

        const hl2 = (high + low) / 2;

        const upperBand =
            hl2 + multiplier * atr[i - 14];

        const lowerBand =
            hl2 - multiplier * atr[i - 14];

        trend.push({

            upperBand,

            lowerBand,

            direction:
    close >= hl2
        ? "BUY"
        : "SELL"

        });

    }

    return trend;

}

module.exports = calculateSupertrend;
