import React, {
  useEffect,
  useState
} from 'react';

const marketData = {
  Indian: {
    Indices: [
      'NIFTY',
      'BANKNIFTY',
      'FINNIFTY',
      'MIDCPNIFTY',
      'SENSEX'
    ],

    Stocks: [
      'RELIANCE',
      'TCS',
      'INFY',
      'SBIN',
      'HDFCBANK',
      'ICICIBANK',
      'ITC',
      'LT',
      'AXISBANK',
      'BAJFINANCE'
    ]
  },

  Forex: {
    Forex: [
      'EURUSD',
      'GBPUSD',
      'USDJPY',
      'AUDUSD',
      'USDCHF'
    ],

    Crypto: [
      'BTCUSDT',
      'ETHUSDT',
      'SOLUSDT',
      'XRPUSDT',
      'DOGEUSDT'
    ]
  }
};

const ClientDashboard = () => {

  const [loading, setLoading] =
    useState(true);

  const [marketType, setMarketType] =
    useState('Indian');

  const [selectedCategory, setSelectedCategory] =
    useState('Indices');

  const [selectedPair, setSelectedPair] =
    useState('');

  const [searchPair, setSearchPair] =
    useState('');

  const [algoActive, setAlgoActive] =
    useState(false);

  const [watchOnly, setWatchOnly] =
    useState(false);

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

const [orderBook, setOrderBook] =
  useState([]);

  const [connectionData, setConnectionData] =
    useState({
      broker: '',
      clientId: '',
      password: '',
      totp: ''
    });

  useEffect(() => {

    const validateLicense =
      async () => {

        const license =
          localStorage.getItem(
            'licenseKey'
          );

        if (!license) {

          window.location.href = '/';

          return;

        }

        try {

          const response =
            await fetch(
              `${process.env.REACT_APP_API_URL}/api/license/activate`,
              {
                method: 'POST',
                headers: {
                  'Content-Type':
                    'application/json'
                },
                body: JSON.stringify({
                  licenseKey:
                    license
                })
              }
            );

          const data =
            await response.json();

          if (!data.success) {

            localStorage.removeItem(
              'licenseKey'
            );

            window.location.href = '/';

          } else {

            setLoading(false);

          }

        } catch (error) {

          window.location.href = '/';

        }

      };

    validateLicense();

fetchBrokerData();

const brokerTimer =
  setInterval(() => {

    fetchBrokerData();

  }, 10000);

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

      const orders =
        data.orders?.data || [];

      setAvailableBalance(
        rms?.availablecash || 0
      );

      setRunningTrades(
        positions.length
      );

      setOrderBook(
        orders
      );

      let totalPL = 0;

      positions.forEach((pos) => {

        totalPL += Number(
          pos.pnl || 0
        );

      });

      setRunningPL(totalPL);

    } catch (error) {

      console.log(error);

    }

};

    const timer =
      setInterval(() => {

        setCurrentTime(
          new Date().toLocaleTimeString()
        );

      }, 1000);

    return () => {

      clearInterval(timer);

    };

  }, []);

   const logout = () => {

  localStorage.removeItem('licenseActivated');
  localStorage.removeItem('licenseKey');
  localStorage.removeItem('brokerConnection');

  window.location.href = '/';

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

  if (loading) {

    return (

      <div className="min-h-screen bg-black flex items-center justify-center text-white text-3xl">

        Validating License...

      </div>

    );

  }

  return (

    <div className="min-h-screen bg-black text-white flex flex-col">

      <header className="border-b border-purple-600 px-10 py-6 bg-zinc-950">

        <div className="flex justify-between items-center">

          <div>

            <h1 className="text-5xl font-bold text-purple-400">
              Welcome to JD-Algo
            </h1>

            <p className="text-zinc-400 mt-2">
              AI Automated Trading Terminal
            </p>

          </div>

          <button
            onClick={logout}
            className="bg-red-600 px-6 py-3 rounded-xl"
          >
            Logout
          </button>

        </div>

        <div className="mt-6 flex gap-4 flex-wrap">

          <div className="bg-zinc-800 px-4 py-2 rounded-full border border-green-500">
            <span className="text-zinc-400">
              Time:
            </span>

            <span className="text-green-400 font-bold ml-2">
              {currentTime}
            </span>
          </div>

          <div className="bg-zinc-800 px-4 py-2 rounded-full border border-blue-500">
            <span className="text-zinc-400">
              Mode:
            </span>

            <span className="text-blue-400 font-bold ml-2">
              {watchOnly
                ? 'WATCH ONLY'
                : 'AUTO EXECUTION'}
            </span>
          </div>

        </div>

      </header>

      <main className="flex-1 p-8 overflow-auto">

        <div className="grid grid-cols-5 gap-4 mb-8">

          <div className="bg-zinc-900 border border-green-600 rounded-2xl p-4 text-center">
            <p className="text-zinc-400 text-sm mb-2">
              Broker
            </p>

            <p className="text-green-400 font-bold text-lg">
              {brokerConnected
                ? 'CONNECTED'
                : 'DISCONNECTED'}
            </p>
          </div>

          <div className="bg-zinc-900 border border-purple-600 rounded-2xl p-4 text-center">
            <p className="text-zinc-400 text-sm mb-2">
              Algo Engine
            </p>

            <p className={`${algoActive ? 'text-green-400' : 'text-red-400'} font-bold text-lg`}>
              {algoActive
                ? 'RUNNING'
                : 'STOPPED'}
            </p>
          </div>

          <div className="bg-zinc-900 border border-yellow-600 rounded-2xl p-4 text-center">
            <p className="text-zinc-400 text-sm mb-2">
              Market Feed
            </p>

            <p className="text-yellow-400 font-bold text-lg">
              LIVE
            </p>
          </div>

          <div className="bg-zinc-900 border border-blue-600 rounded-2xl p-4 text-center">
            <p className="text-zinc-400 text-sm mb-2">
              License
            </p>

            <p className="text-blue-400 font-bold text-lg">
              ACTIVE
            </p>
          </div>

          <div className="bg-zinc-900 border border-red-600 rounded-2xl p-4 text-center">
            <p className="text-zinc-400 text-sm mb-2">
              Server
            </p>

            <p className="text-red-400 font-bold text-lg">
              HEALTHY
            </p>
          </div>

        </div>

        <div className="grid grid-cols-2 gap-6 mb-8">

          <div className="bg-zinc-900 border border-purple-600 rounded-3xl p-8">

            <h2 className="text-3xl font-bold mb-6 text-purple-400">
              Market Selection
            </h2>

            <div className="flex gap-4 mb-6">

              <button
                onClick={() => {
                  setMarketType('Indian');
                  setSelectedCategory(
                    'Indices'
                  );
                }}
                className={`flex-1 py-4 rounded-2xl text-xl ${marketType === 'Indian' ? 'bg-purple-600' : 'bg-zinc-800'}`}
              >
                Indian Market
              </button>

              <button
                onClick={() => {
                  setMarketType('Forex');
                  setSelectedCategory(
                    'Forex'
                  );
                }}
                className={`flex-1 py-4 rounded-2xl text-xl ${marketType === 'Forex' ? 'bg-purple-600' : 'bg-zinc-800'}`}
              >
                Forex / Crypto
              </button>

            </div>

            <select
              value={selectedCategory}
              onChange={(e) =>
                setSelectedCategory(
                  e.target.value
                )
              }
              className="w-full bg-zinc-800 p-4 rounded-xl outline-none mb-4"
            >

              {Object.keys(
                marketData[marketType]
              ).map((category) => (

                <option
                  key={category}
                  value={category}
                >
                  {category}
                </option>

              ))}

            </select>

            <input
              type="text"
              placeholder="Search Pair..."
              value={searchPair}
              onChange={(e) =>
                setSearchPair(
                  e.target.value
                )
              }
              className="w-full bg-zinc-800 p-4 rounded-xl outline-none mb-4"
            />

            <select
              value={selectedPair}
              onChange={(e) =>
                setSelectedPair(
                  e.target.value
                )
              }
              className="w-full bg-zinc-800 p-4 rounded-xl outline-none mb-6"
            >

              <option value="">
                Auto Market Scan Mode
              </option>

              {marketData[marketType][selectedCategory]
                .filter((pair) =>
                  pair
                    .toLowerCase()
                    .includes(
                      searchPair.toLowerCase()
                    )
                )
                .map((pair) => (

                  <option
                    key={pair}
                    value={pair}
                  >
                    {pair}
                  </option>

                ))}

            </select>

            <div className="flex gap-4">

              <button
                onClick={() =>
                  setAlgoActive(
                    !algoActive
                  )
                }
                className={`${algoActive ? 'bg-red-600' : 'bg-green-600'} px-6 py-3 rounded-xl text-lg font-bold`}
              >
                {algoActive
                  ? 'Stop Algo'
                  : 'Activate Algo'}
              </button>

              <button
                onClick={() =>
                  setWatchOnly(
                    !watchOnly
                  )
                }
                className={`${watchOnly ? 'bg-blue-600' : 'bg-zinc-700'} px-6 py-3 rounded-xl text-lg font-bold`}
              >
                Watch Only
              </button>

            </div>

          </div>

          <div className="bg-zinc-900 border border-green-600 rounded-3xl p-8">

            <h2 className="text-3xl font-bold mb-6 text-green-400">
              Broker Connection Center
            </h2>

            <div className="space-y-4">

              <select
                value={connectionData.broker}
                onChange={(e) =>
                  setConnectionData({
                    ...connectionData,
                    broker:
                      e.target.value
                  })
                }
                className="w-full bg-zinc-800 p-4 rounded-xl outline-none"
              >

                <option value="">
                  Select Broker
                </option>

                <option value="AngelOne">
                  Angel One
                </option>

              </select>

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
                className="w-full bg-zinc-800 p-4 rounded-xl outline-none"
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
                className="w-full bg-zinc-800 p-4 rounded-xl outline-none"
              />

              <input
                type="text"
                placeholder="Current TOTP"
                value={connectionData.totp}
                onChange={(e) =>
                  setConnectionData({
                    ...connectionData,
                    totp:
                      e.target.value
                  })
                }
                className="w-full bg-zinc-800 p-4 rounded-xl outline-none"
              />

              <button
                onClick={connectBroker}
                className="w-full bg-green-600 hover:bg-green-700 p-4 rounded-xl text-lg font-bold"
              >
                {brokerConnected
                  ? 'Connected Successfully'
                  : 'Connect Broker'}
              </button>

            </div>

          </div>

        </div>

        <div className="grid grid-cols-4 gap-6 mb-8">

          <div className="bg-zinc-900 border border-green-500 rounded-2xl p-6">
            <h3 className="text-zinc-400 mb-3">
              Today P/L
            </h3>

            <p className="text-4xl font-bold text-green-400">
              ₹{runningPL.toLocaleString()}
            </p>
          </div>

          <div className="bg-zinc-900 border border-cyan-500 rounded-2xl p-6">

  <h3 className="text-zinc-400 mb-3">
    Available Balance
  </h3>

  <p className="text-4xl font-bold text-cyan-400">
    ₹{Number(availableBalance).toLocaleString()}
  </p>

</div>

          <div className="bg-zinc-900 border border-yellow-500 rounded-2xl p-6">
            <h3 className="text-zinc-400 mb-3">
              Running Trades
            </h3>

            <p className="text-4xl font-bold text-yellow-400">
              {runningTrades}
            </p>
          </div>

          <div className="bg-zinc-900 border border-blue-500 rounded-2xl p-6">
            <h3 className="text-zinc-400 mb-3">
              Win Rate
            </h3>

            <p className="text-4xl font-bold text-blue-400">
              78%
            </p>
          </div>

          <div className="bg-zinc-900 border border-purple-500 rounded-2xl p-6">
            <h3 className="text-zinc-400 mb-3">
              Mode
            </h3>

            <p className="text-3xl font-bold text-purple-400">
              {watchOnly
                ? 'WATCH'
                : 'LIVE'}
            </p>
          </div>

        </div>

      </main>

      <footer className="border-t border-zinc-800 text-center py-5 text-zinc-500 bg-zinc-950">

        Powered by Xyca Technologies Private Limited

      </footer>

    </div>

  );

};

export default ClientDashboard;