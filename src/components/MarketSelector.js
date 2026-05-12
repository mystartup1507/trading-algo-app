import React from 'react';

import {
  Globe,
  Landmark
} from 'lucide-react';

const MarketSelector = ({
  selectedMarket,
  setSelectedMarket,
  selectedBroker,
  setSelectedBroker,
  tradingMode,
  setTradingMode,
  selectedPair,
  setSelectedPair
}) => {

  const indianBrokers = [
    {
      label: 'Angel One',
      value: 'angel'
    },
    {
      label: 'Dhan',
      value: 'dhan'
    }
  ];

  const forexBrokers = [
    {
      label: 'MT4',
      value: 'mt4'
    },
    {
      label: 'MT5',
      value: 'mt5'
    }
  ];

  return (

    <div className="bg-zinc-900 border border-purple-500/30 rounded-3xl p-8 space-y-6">

      <h2 className="text-3xl font-bold text-purple-400">
        Market Selection
      </h2>

      <div className="grid grid-cols-2 gap-4">

        <button
          onClick={() => setSelectedMarket('indian')}
          className={
            selectedMarket === 'indian'
              ? 'bg-purple-600 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
              : 'bg-zinc-800 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
          }
        >
          <Landmark size={18} />
          Indian Market
        </button>

        <button
          onClick={() => setSelectedMarket('forex')}
          className={
            selectedMarket === 'forex'
              ? 'bg-cyan-600 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
              : 'bg-zinc-800 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
          }
        >
          <Globe size={18} />
          Forex/Crypto
        </button>

      </div>

      <select
        value={selectedBroker}
        onChange={(e) =>
          setSelectedBroker(e.target.value)
        }
        className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
      >

        {
          (
            selectedMarket === 'indian'
              ? indianBrokers
              : forexBrokers
          ).map((broker) => (

            <option
              key={broker.value}
              value={broker.value}
            >
              {broker.label}
            </option>

          ))
        }

      </select>

      <div className="grid grid-cols-2 gap-4">

        <button
          onClick={() => setTradingMode('auto')}
          className={
            tradingMode === 'auto'
              ? 'bg-green-600 p-4 rounded-2xl font-bold'
              : 'bg-zinc-800 p-4 rounded-2xl font-bold'
          }
        >
          Auto Mode
        </button>

        <button
          onClick={() => setTradingMode('manual')}
          className={
            tradingMode === 'manual'
              ? 'bg-yellow-600 p-4 rounded-2xl font-bold'
              : 'bg-zinc-800 p-4 rounded-2xl font-bold'
          }
        >
          Manual Pair
        </button>

      </div>

      {
        tradingMode === 'manual' && (

          <input
            type="text"
            placeholder={
              selectedMarket === 'indian'
                ? 'Search Indian Pair'
                : 'Search Forex/Crypto Pair'
            }
            value={selectedPair}
            onChange={(e) =>
              setSelectedPair(e.target.value)
            }
            className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
          />

        )
      }

    </div>

  );

};

export default MarketSelector;