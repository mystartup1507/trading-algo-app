import React from 'react';

import {
  TrendingUp,
  Wallet,
  Activity,
  Clock3
} from 'lucide-react';

const StatsCards = ({
  runningPL,
  availableBalance,
  runningTrades,
  currentTime
}) => {

  return (

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

      <div className="bg-zinc-900 border border-green-500/40 rounded-3xl p-8">

        <div className="flex justify-between items-center mb-5">

          <h3 className="text-zinc-400">
            Today P/L
          </h3>

          <TrendingUp className="text-green-400" />

        </div>

        <p className="text-5xl font-black text-green-400">
          ₹{runningPL}
        </p>

      </div>

      <div className="bg-zinc-900 border border-cyan-500/40 rounded-3xl p-8">

        <div className="flex justify-between items-center mb-5">

          <h3 className="text-zinc-400">
            Available Balance
          </h3>

          <Wallet className="text-cyan-400" />

        </div>

        <p className="text-5xl font-black text-cyan-400">
          ₹{availableBalance}
        </p>

      </div>

      <div className="bg-zinc-900 border border-yellow-500/40 rounded-3xl p-8">

        <div className="flex justify-between items-center mb-5">

          <h3 className="text-zinc-400">
            Running Trades
          </h3>

          <Activity className="text-yellow-400" />

        </div>

        <p className="text-5xl font-black text-yellow-400">
          {runningTrades}
        </p>

      </div>

      <div className="bg-zinc-900 border border-purple-500/40 rounded-3xl p-8">

        <div className="flex justify-between items-center mb-5">

          <h3 className="text-zinc-400">
            Current Time
          </h3>

          <Clock3 className="text-purple-400" />

        </div>

        <p className="text-4xl font-black text-purple-400">
          {currentTime}
        </p>

      </div>

    </div>

  );

};

export default StatsCards;