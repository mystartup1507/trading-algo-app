const { RSI } = require("technicalindicators");

function calculateRSI(closes) {

    return RSI.calculate({

        period: 14,

        values: closes

    });

}

module.exports = calculateRSI;
