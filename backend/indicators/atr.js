const { ATR } = require("technicalindicators");

function calculateATR(candles) {

    const high = candles.map(c => Number(c[2]));
    const low = candles.map(c => Number(c[3]));
    const close = candles.map(c => Number(c[4]));

    return ATR.calculate({

        high,

        low,

        close,

        period: 14

    });

}

module.exports = calculateATR;
