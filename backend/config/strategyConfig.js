module.exports = {

    strategy: "INTRADAY",

    timeframe: "FIVE_MINUTE",

    indicators: {

        emaFast: 9,

        emaSlow: 21,

        emaTrend: 50,

        rsiPeriod: 14,

        atrPeriod: 14,

        supertrendMultiplier: 3,

        supertrendPeriod: 10

    },

    risk: {

        riskPerTrade: 1,

        maxTradesPerDay: 5,

        maxDailyLoss: 2000,

        riskReward: 2,

        trailingSL: true

    },

    ai: {

        confidenceThreshold: 60,

        minimumVolumeMultiplier: 1.5,
        
        testMode: true

    }

};
