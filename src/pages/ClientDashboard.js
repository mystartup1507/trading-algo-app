import React, { useEffect, useState } from 'react';

import {
  Activity,
  Wifi,
  ShieldCheck,
  Server,
  Wallet,
  TrendingUp,
  Clock3,
  LogOut,
  PlugZap,
  Unplug,
  Globe,
  Landmark,
  Play,
  Square
} from 'lucide-react';

const ClientDashboard = () => {

  const [brokerConnected, setBrokerConnected] = useState(false);
  const [currentTime, setCurrentTime] = useState('');
  const [runningPL] = useState(0);
  const [availableBalance] = useState(0);
  const [runningTrades] = useState(0);

  const [selectedMarket, setSelectedMarket] = useState('indian');
  const [selectedBroker, setSelectedBroker] = useState('angel');
  const [tradingMode, setTradingMode] = useState('auto');
  const [selectedPair, setSelectedPair] = useState('');
  const [algoRunning, setAlgoRunning] = useState(false);

  const [connectionData, setConnectionData] = useState({
    clientId: '',
    password: '',
    totp: '',
    server: ''
  });

  useEffect(() => {

    const activated = localStorage.getItem('licenseActivated');

    if (activated !== 'true') {
      window.location.href = '/';
      return;
    }

    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(timer);

  }, []);

  useEffect(() => {

    if (selectedMarket === 'indian') {
      setSelectedBroker('angel');
    } else {
      setSelectedBroker('mt5');
    }

  }, [selectedMarket]);

  const logout = () => {

    localStorage.removeItem('licenseActivated');
    localStorage.removeItem('licenseKey');
    localStorage.removeItem('brokerConnection');

    window.location.href = '/';

  };

  const connectBroker = async () => {

    try {

      if (!connectionData.clientId || !connectionData.password) {
        alert('Please fill broker credentials');
        return;
      }

      setBrokerConnected(true);

      alert('Broker Connected Successfully');

    } catch (error) {

      alert('Connection Error');

    }

  };

  const disconnectBroker = () => {

    localStorage.removeItem('brokerConnection');

    setBrokerConnected(false);

    alert('Broker Disconnected');

  };

  const toggleAlgo = () => {

    if (tradingMode === 'manual' && !selectedPair) {
      alert('Please enter pair/symbol');
      return;
    }

    setAlgoRunning(!algoRunning);

  };

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

    <div className="min-h-screen bg-black text-white">

      <header className="border-b border-purple-500/30 bg-zinc-950/80 px-8 py-6">

        <div className="flex justify-between items-center">

          <div>

            <h1 className="text-5xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 text-transparent bg-clip-text">
              JD-Algo
            </h1>

            <p className="text-zinc-400 mt-2">
              Multi-Market Execution Terminal
            </p>

          </div>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-2xl flex items-center gap-2"
          >
            <LogOut size={18} />
            Logout
          </button>

        </div>

      </header>

      <main className="p-8 space-y-8">

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">

          <div className="bg-zinc-900 border border-green-500/40 rounded-3xl p-6">

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-zinc-400 text-sm">Broker</h3>
              <PlugZap className="text-green-400" />
            </div>

            <p className={brokerConnected ? 'text-2xl font-bold text-green-400' : 'text-2xl font-bold text-red-400'}>
              {brokerConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </p>

          </div>

          <div className="bg-zinc-900 border border-purple-500/40 rounded-3xl p-6">

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-zinc-400 text-sm">Algo Engine</h3>
              <Activity className="text-purple-400" />
            </div>

            <p className={algoRunning ? 'text-2xl font-bold text-green-400' : 'text-2xl font-bold text-red-400'}>
              {algoRunning ? 'RUNNING' : 'STOPPED'}
            </p>

          </div>

          <div className="bg-zinc-900 border border-yellow-500/40 rounded-3xl p-6">

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-zinc-400 text-sm">Market Feed</h3>
              <Wifi className="text-yellow-400" />
            </div>

            <p className="text-2xl font-bold text-yellow-400">LIVE</p>

          </div>

          <div className="bg-zinc-900 border border-blue-500/40 rounded-3xl p-6">

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-zinc-400 text-sm">License</h3>
              <ShieldCheck className="text-blue-400" />
            </div>

            <p className="text-2xl font-bold text-blue-400">ACTIVE</p>

          </div>

          <div className="bg-zinc-900 border border-red-500/40 rounded-3xl p-6">

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-zinc-400 text-sm">Server</h3>
              <Server className="text-red-400" />
            </div>

            <p className="text-2xl font-bold text-red-400">HEALTHY</p>

          </div>

        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          <div className="bg-zinc-900 border border-purple-500/30 rounded-3xl p-8 space-y-6">

            <h2 className="text-3xl font-bold text-purple-400">
              Market Selection
            </h2>

            <div className="grid grid-cols-2 gap-4">

              <button
                onClick={() => setSelectedMarket('indian')}
                className={selectedMarket === 'indian'
                  ? 'bg-purple-600 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
                  : 'bg-zinc-800 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'}
              >
                <Landmark size={18} />
                Indian Market
              </button>

              <button
                onClick={() => setSelectedMarket('forex')}
                className={selectedMarket === 'forex'
                  ? 'bg-cyan-600 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'
                  : 'bg-zinc-800 p-4 rounded-2xl font-bold flex items-center justify-center gap-2'}
              >
                <Globe size={18} />
                Forex/Crypto
              </button>

            </div>

            <select
              value={selectedBroker}
              onChange={(e) => setSelectedBroker(e.target.value)}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
            >

              {(selectedMarket === 'indian' ? indianBrokers : forexBrokers).map((broker) => (
                <option
                  key={broker.value}
                  value={broker.value}
                >
                  {broker.label}
                </option>
              ))}

            </select>

            <div className="grid grid-cols-2 gap-4">

              <button
                onClick={() => setTradingMode('auto')}
                className={tradingMode === 'auto'
                  ? 'bg-green-600 p-4 rounded-2xl font-bold'
                  : 'bg-zinc-800 p-4 rounded-2xl font-bold'}
              >
                Auto Mode
              </button>

              <button
                onClick={() => setTradingMode('manual')}
                className={tradingMode === 'manual'
                  ? 'bg-yellow-600 p-4 rounded-2xl font-bold'
                  : 'bg-zinc-800 p-4 rounded-2xl font-bold'}
              >
                Manual Pair
              </button>

            </div>

            {tradingMode === 'manual' && (
              <input
                type="text"
                placeholder={selectedMarket === 'indian'
                  ? 'Search Indian Pair'
                  : 'Search Forex/Crypto Pair'}
                value={selectedPair}
                onChange={(e) => setSelectedPair(e.target.value)}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
              />
            )}

          </div>

          <div className="bg-zinc-900 border border-green-500/30 rounded-3xl p-8 space-y-5">

            <h2 className="text-3xl font-bold text-green-400">
              Broker Connection
            </h2>

            <input
              type="text"
              placeholder="Client/Login ID"
              value={connectionData.clientId}
              onChange={(e) => setConnectionData({
                ...connectionData,
                clientId: e.target.value
              })}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
            />

            <input
              type="password"
              placeholder="PIN / Password"
              value={connectionData.password}
              onChange={(e) => setConnectionData({
                ...connectionData,
                password: e.target.value
              })}
              className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
            />

            {selectedMarket === 'forex' && (
              <input
                type="text"
                placeholder="MT4/MT5 Server"
                value={connectionData.server}
                onChange={(e) => setConnectionData({
                  ...connectionData,
                  server: e.target.value
                })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
              />
            )}

            {selectedMarket === 'indian' && (
              <input
                type="text"
                placeholder="Current TOTP"
                value={connectionData.totp}
                onChange={(e) => setConnectionData({
                  ...connectionData,
                  totp: e.target.value
                })}
                className="w-full bg-zinc-800 border border-zinc-700 rounded-2xl p-4 outline-none"
              />
            )}

            {brokerConnected ? (
              <button
                onClick={disconnectBroker}
                className="w-full bg-red-600 hover:bg-red-700 rounded-2xl p-4 font-bold flex items-center justify-center gap-2"
              >
                <Unplug size={18} />
                Disconnect Broker
              </button>
            ) : (
              <button
                onClick={connectBroker}
                className="w-full bg-green-600 hover:bg-green-700 rounded-2xl p-4 font-bold flex items-center justify-center gap-2"
              >
                <PlugZap size={18} />
                Connect Broker
              </button>
            )}

            {algoRunning ? (
              <button
                onClick={toggleAlgo}
                className="w-full bg-red-600 hover:bg-red-700 rounded-2xl p-4 font-bold flex items-center justify-center gap-2"
              >
                <Square size={18} />
                Stop Algo
              </button>
            ) : (
              <button
                onClick={toggleAlgo}
                className="w-full bg-cyan-600 hover:bg-cyan-700 rounded-2xl p-4 font-bold flex items-center justify-center gap-2"
              >
                <Play size={18} />
                Start Algo
              </button>
            )}

          </div>

        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

          <div className="bg-zinc-900 border border-green-500/40 rounded-3xl p-8">

            <div className="flex justify-between items-center mb-5">
              <h3 className="text-zinc-400">Today P/L</h3>
              <TrendingUp className="text-green-400" />
            </div>

            <p className="text-5xl font-black text-green-400">
              ₹{runningPL}
            </p>

          </div>

          <div className="bg-zinc-900 border border-cyan-500/40 rounded-3xl p-8">

            <div className="flex justify-between items-center mb-5">
              <h3 className="text-zinc-400">Available Balance</h3>
              <Wallet className="text-cyan-400" />
            </div>

            <p className="text-5xl font-black text-cyan-400">
              ₹{availableBalance}
            </p>

          </div>

          <div className="bg-zinc-900 border border-yellow-500/40 rounded-3xl p-8">

            <div className="flex justify-between items-center mb-5">
              <h3 className="text-zinc-400">Running Trades</h3>
              <Activity className="text-yellow-400" />
            </div>

            <p className="text-5xl font-black text-yellow-400">
              {runningTrades}
            </p>

          </div>

          <div className="bg-zinc-900 border border-purple-500/40 rounded-3xl p-8">

            <div className="flex justify-between items-center mb-5">
              <h3 className="text-zinc-400">Current Time</h3>
              <Clock3 className="text-purple-400" />
            </div>

            <p className="text-4xl font-black text-purple-400">
              {currentTime}
            </p>

          </div>

        </div>

      </main>

    </div>

  );

};

export default ClientDashboard;
