import React from 'react';

const AIEngineStatus = () => {

  const marketCondition = 'TRENDING';
  const aiConfidence = '82%';
  const marketBias = 'BULLISH';
  const aiStatus = 'SCANNING';

  return (

    <div className="bg-zinc-900 border border-cyan-500/30 rounded-3xl p-8 space-y-6">

      <div className="flex justify-between items-center">

        <div>

          <h2 className="text-3xl font-bold text-cyan-400">
            AI Engine
          </h2>

          <p className="text-zinc-500 mt-1">
            Autonomous Market Intelligence
          </p>

        </div>

        <div className="h-4 w-4 rounded-full bg-green-400 animate-pulse"></div>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        <div className="bg-zinc-800 rounded-2xl p-5 border border-zinc-700">

          <p className="text-zinc-500 text-sm mb-2">
            Market Condition
          </p>

          <h3 className="text-2xl font-bold text-green-400">
            {marketCondition}
          </h3>

        </div>

        <div className="bg-zinc-800 rounded-2xl p-5 border border-zinc-700">

          <p className="text-zinc-500 text-sm mb-2">
            AI Confidence
          </p>

          <h3 className="text-2xl font-bold text-cyan-400">
            {aiConfidence}
          </h3>

        </div>

        <div className="bg-zinc-800 rounded-2xl p-5 border border-zinc-700">

          <p className="text-zinc-500 text-sm mb-2">
            Current Bias
          </p>

          <h3 className="text-2xl font-bold text-yellow-400">
            {marketBias}
          </h3>

        </div>

        <div className="bg-zinc-800 rounded-2xl p-5 border border-zinc-700">

          <p className="text-zinc-500 text-sm mb-2">
            AI Status
          </p>

          <h3 className="text-2xl font-bold text-purple-400">
            {aiStatus}
          </h3>

        </div>

      </div>

    </div>

  );

};

export default AIEngineStatus;