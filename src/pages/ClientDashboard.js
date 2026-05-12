import React, {
  useEffect,
  useState
} from 'react';

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
  Unplug
} from 'lucide-react';

const ClientDashboard = () => {

  const [brokerConnected, setBrokerConnected] =
    useState(false);

  const [currentTime, setCurrentTime] =
    useState('');

  const [runningPL, setRunningPL] =
    useState(0);

  const [availableBalance, setAvailableBalance] =
    useState(0);

  const [runningTrades, setRunningTrades] =
    useState(0);

  const [connectionData, setConnectionData] =
    useState({
      clientId: '',
      password: '',
      totp: ''
    });

  useEffect(() => {

    const activated =
      localStorage.getItem(
        'licenseActivated'
      );

    if (activated !== 'true') {

      window.location.href = '/';

      return;

    }

    const fetchBrokerData =
      async () => {

        try {

          const brokerData =
            JSON.parse(
              localStorage.getItem(
                'brokerConnection'
              )
            );

          if (
            !brokerData ||
            !brokerData.session
          ) return;

          setBrokerConnected(true);

          const response =
            await fetch(
              `${process.env.REACT_APP_API_URL}/api/broker/data`,
              {
                method: 'POST',
                headers: {
                  'Content-Type':
                    'application/json'
                },
                body: JSON.stringify({
                  apiKey:
                    'QTgnsVLk',

                  jwtToken:
                    brokerData.session.jwtToken,

                  refreshToken:
                    brokerData.session.refreshToken,

                  feedToken:
                    brokerData.session.feedToken
                })
              }
            );

          const data =
            await response.json();

          if (!data.success) return;

          const rms =
            data.rms?.data;

          const positions =
            data.positions?.data || [];

          let totalPL = 0;

          positions.forEach((pos) => {

            totalPL += Number(
              pos.pnl || 0
            );

          });

          setRunningPL(totalPL);

          setAvailableBalance(
            rms?.availablecash || 0
          );

          setRunningTrades(
            positions.length
          );

        } catch (error) {

          console.log(error);

        }

      };

    fetchBrokerData();

    const brokerTimer =
      setInterval(() => {

        fetchBrokerData();

      }, 10000);

    const timer =
      setInterval(() => {

        setCurrentTime(
          new Date().toLocaleTimeString()
        );

      }, 1000);

    return () => {

      clearInterval(timer);
      clearInterval(brokerTimer);

    };

  }, []);

  const logout = () => {

    localStorage.removeItem(
      'licenseActivated'
    );

    localStorage.removeItem(
      'licenseKey'
    );

    localStorage.removeItem(
      'brokerConnection'
    );

    window.location.href = '/';

  };

  const disconnectBroker =
    () => {

      localStorage.removeItem(
        'brokerConnection'
      );

      setBrokerConnected(false);

      alert(
        'Broker Disconnected'
      );

    };

  const connectBroker =
    async () => {

      try {

        if (
          !connectionData.clientId ||
          !connectionData.password ||
          !connectionData.totp
        ) {

          alert(
            'Please fill all broker details'
          );

          return;

        }

        const response =
          await fetch(
            `${process.env.REACT_APP_API_URL}/api/broker/connect/angel`,
            {
              method: 'POST',
              headers: {
                'Content-Type':
                  'application/json'
              },
              body: JSON.stringify({
                apiKey:
                  'QTgnsVLk',

                clientId:
                  connectionData.clientId,

                password:
                  connectionData.password,

                totp:
                  connectionData.totp
              })
            }
          );

        const data =
          await response.json();

        if (!data.success) {

          alert(
            data.message ||
            'Broker connection failed'
          );

          return;

        }

        localStorage.setItem(
          'brokerConnection',
          JSON.stringify({
            ...connectionData,
            session:
              data.data
          })
        );

        setBrokerConnected(true);

        alert(
          'Angel One Connected Successfully'
        );

      } catch (error) {

        alert(
          'Connection Error'
        );

      }

    };

  return (

    <div className="min-h-screen bg-black text-white overflow-hidden">

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,#7c3aed22,transparent_25%),radial-gradient(circle_at_bottom_right,#06b6d422,transparent_25%)]"></div>

      <div className="relative z-10">

        <header className="border-b border-purple-500/30 backdrop-blur-xl bg-zinc-950/70 px-8 py-6 sticky top-0 z-50">

          <div className="flex items-center justify-between">

            <div>

              <h1 className="text-5xl font-black bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 text-transparent bg-clip-text">
                JD-Algo
              </h1>

              <p className="text-zinc-400 mt-2 text-lg">
                AI Powered Trading Infrastructure
              </p>

            </div>

            <button
              onClick={logout}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-700 px-6 py-3 rounded-2xl transition-all duration-300 shadow-lg shadow-red-600/30"
            >
              <LogOut size={20} />
              Logout
            </button>

          </div>

        </header>

        <main className="p-8 space-y-8">

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">

            <div className="bg-zinc-900/60 border border-green-500/40 backdrop-blur-2xl rounded-3xl p-6 shadow-lg shadow-green-500/10">

  <div className="flex justify-between items-center mb-4">

    <h3 className="text-zinc-400 text-sm">
      Broker
    </h3>

    <PlugZap className="text-green-400" />

  </div>

  <p
    className={
      brokerConnected
        ? 'text-2xl font-bold text-green-400'
        : 'text-2xl font-bold text-red-400'
    }
  >
    {
      brokerConnected
        ? 'CONNECTED'
        : 'DISCONNECTED'
    }
  </p>

</div>

            </div>

            <div className="bg-zinc-900/60 border border-purple-500/40 backdrop-blur-2xl rounded-3xl p-6 shadow-lg shadow-purple-500/10">

              <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-400 text-sm">
                  Algo Engine
                </h3>

                <Activity className="text-purple-400" />
              </div>

              <p className="text-2xl font-bold text-red-400">
                STOPPED
              </p>

            </div>

            <div className="bg-zinc-900/60 border border-yellow-500/40 backdrop-blur-2xl rounded-3xl p-6 shadow-lg shadow-yellow-500/10">

              <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-400 text-sm">
                  Market Feed
                </h3>

                <Wifi className="text-yellow-400" />
              </div>

              <p className="text-2xl font-bold text-yellow-400">
                LIVE
              </p>

            </div>

            <div className="bg-zinc-900/60 border border-blue-500/40 backdrop-blur-2xl rounded-3xl p-6 shadow-lg shadow-blue-500/10">

              <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-400 text-sm">
                  License
                </h3>

                <ShieldCheck className="text-blue-400" />
              </div>

              <p className="text-2xl font-bold text-blue-400">
                ACTIVE
              </p>

            </div>

            <div className="bg-zinc-900/60 border border-red-500/40 backdrop-blur-2xl rounded-3xl p-6 shadow-lg shadow-red-500/10">

              <div className="flex justify-between items-center mb-4">
                <h3 className="text-zinc-400 text-sm">
                  Server
                </h3>

                <Server className="text-red-400" />
              </div>

              <p className="text-2xl font-bold text-red-400">
                HEALTHY
              </p>

            </div>

          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            <div className="bg-zinc-900/60 border border-green-500/30 backdrop-blur-2xl rounded-[32px] p-8 shadow-2xl shadow-green-500/10">

              <h2 className="text-4xl font-bold text-green-400 mb-8">
                Broker Connection
              </h2>

              <div className="space-y-5">

                <input
                  type="text"
                  placeholder="Angel Client ID"
                  value={connectionData.clientId}
                  onChange={(e) =>
                    setConnectionData({
                      ...connectionData,
                      clientId:
                        e.target.value
                    })
                  }
                  className="w-full bg-zinc-800/70 border border-zinc-700 focus:border-green-400 rounded-2xl p-5 outline-none text-lg"
                />

                <input
                  type="password"
                  placeholder="4 Digit PIN"
                  value={connectionData.password}
                  onChange={(e) =>
                    setConnectionData({
                      ...connectionData,
                      password:
                        e.target.value
                    })
                  }
                  className="w-full bg-zinc-800/70 border border-zinc-700 focus:border-green-400 rounded-2xl p-5 outline-none text-lg"
                />

                <input
                  type="text"
                  placeholder="Current TOTP"
                  value={connectionData.totp}