function calculateVWAP(candles) {

    let cumulativePV = 0;
    let cumulativeVolume = 0;

    const values = [];

    for (const candle of candles) {

        const high = Number(candle[2]);
        const low = Number(candle[3]);
        const close = Number(candle[4]);
        const volume = Number(candle[5]);

        const typicalPrice =
            (high + low + close) / 3;

        cumulativePV +=
            typicalPrice * volume;

        cumulativeVolume +=
            volume;

        values.push(
            cumulativePV / cumulativeVolume
        );

    }

    return values;

}

module.exports = calculateVWAP;
