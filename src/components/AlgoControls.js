import React from 'react';

const AlgoControls = ({
  algoSettings,
  setAlgoSettings
}) => {

  return (

    <div className="bg-zinc-900 border border-cyan-500/30 rounded-3xl p-8 space-y-6">

      <h2 className="text-3xl font-bold text-cyan-400">
        Algo Controls
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

        <div>

          <label className="text-zinc-400 block mb-2">
            Risk Per Trade (%)
          </label>

          <input
            type="number"
            value={algoSettings.riskPercent}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                riskPercent: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        </div>

        <div>

          <label className="text-zinc-400 block mb-2">
            Lot Size
          </label>

          <input
            type="number"
            value={algoSettings.lotSize}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                lotSize: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        </div>

        <div>

          <label className="text-zinc-400 block mb-2">
            Stop Loss (Pips/Points)
          </label>

          <input
            type="number"
            value={algoSettings.stopLoss}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                stopLoss: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        </div>

        <div>

          <label className="text-zinc-400 block mb-2">
            Take Profit (Pips/Points)
          </label>

          <input
            type="number"
            value={algoSettings.takeProfit}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                takeProfit: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        </div>

        <div>

          <label className="text-zinc-400 block mb-2">
            Max Open Trades
          </label>

          <input
            type="number"
            value={algoSettings.maxTrades}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                maxTrades: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        </div>

        <div>

          <label className="text-zinc-400 block mb-2">
            Trade Direction
          </label>

          <select
            value={algoSettings.tradeDirection}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                tradeDirection: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          >
            <option value="both">
              Buy & Sell
            </option>

            <option value="buy">
              Buy Only
            </option>

            <option value="sell">
              Sell Only
            </option>

          </select>

        </div>

        <div className="md:col-span-2">

          <label className="text-zinc-400 block mb-2">
            Confidence Mode
          </label>

          <select
            value={algoSettings.confidenceMode}
            onChange={(e) =>
              setAlgoSettings({
                ...algoSettings,
                confidenceMode: e.target.value
              })
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          >
            <option value="safe">
              Safe Mode
            </option>

            <option value="balanced">
              Balanced Mode
            </option>

            <option value="aggressive">
              Aggressive Mode
            </option>

          </select>

        </div>

      </div>

    </div>

  );

};

export default AlgoControls;