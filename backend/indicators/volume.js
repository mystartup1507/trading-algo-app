function analyzeVolume(candles) {

    const volumes =
        candles.map(c => Number(c[5]));

    const averageVolume =
        volumes.reduce(
            (a, b) => a + b,
            0
        ) / volumes.length;

    const currentVolume =
        volumes.at(-1);

    return {

        averageVolume,

        currentVolume,

        highVolume:
            currentVolume >
            averageVolume * 1.5

    };

}

module.exports = analyzeVolume;
