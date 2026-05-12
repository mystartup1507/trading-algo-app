import React from 'react';

const ActiveTrades = () => {

  const trades = [];

  return (

    <div className="bg-zinc-900 border border-yellow-500/30 rounded-3xl p-8 space-y-6">

      <div className="flex justify-between items-center">

        <div>

          <h2 className="text-3xl font-bold text-yellow-400">
            Active Trades
          </h2>

          <p className="text-zinc-500 mt-1">
            Live AI Managed Positions
          </p>

        </div>

        <div className="h-4 w-4 rounded-full bg-green-400 animate-pulse"></div>

      </div>

      <div className="space-y-4">

        {trades.length === 0 ? (

          <div className="bg-zinc-800 border border-zinc-700 rounded-2xl p-12 text-center">

            <h3 className="text-3xl font-bold text-zinc-400 mb-4">
              No Active Trades
            </h3>

            <p className="text-zinc-500">
              AI Engine is scanning markets for high probability opportunities.
            </p>

          </div>

        ) : (

          trades.map((trade, index) => (

            <div
              key={index}
              className="bg-zinc-800 border border-zinc-700 rounded-2xl p-5"
            >

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 items-center">

                <div>

                  <p className="text-zinc-500 text-sm">
                    Pair
                  </p>

                  <h3 className="text-xl font-bold text-white">
                    {trade.pair}
                  </h3>

                </div>

                <div>

                  <p className="text-zinc-500 text-sm">
                    Type
                  </p>

                  <h3 className={
                    trade.type === 'BUY'
                      ? 'text-xl font-bold text-green-400'
                      : 'text-xl font-bold text-red-400'
                  }>
                    {trade.type}
                  </h3>

                </div>

                <div>

                  <p className="text-zinc-500 text-sm">
                    Entry
                  </p>

                  <h3 className="text-xl font-bold text-cyan-400">
                    {trade.entry}
                  </h3>

                </div>

                <div>

                  <p className="text-zinc-500 text-sm">
                    P/L
                  </p>

                  <h3 className="text-xl font-bold text-green-400">
                    {trade.pnl}
                  </h3>

                </div>

                <div>

                  <p className="text-zinc-500 text-sm">
                    Status
                  </p>

                  <h3 className="text-xl font-bold text-yellow-400">
                    {trade.status}
                  </h3>

                </div>

              </div>

            </div>

          ))

        )}

      </div>

    </div>

  );

};

export default ActiveTrades;