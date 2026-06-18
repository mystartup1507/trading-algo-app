const { EMA } = require("technicalindicators");

function calculateEMA(closes) {

    return {

        ema9: EMA.calculate({
            period: 9,
            values: closes
        }),

        ema21: EMA.calculate({
            period: 21,
            values: closes
        }),

        ema50: EMA.calculate({
            period: 50,
            values: closes
        }),

        ema200: EMA.calculate({
            period: 200,
            values: closes
        })

    };

}

module.exports = calculateEMA;
