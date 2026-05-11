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
      'SENSEX',
      'BANKEX'
    ],
    Stocks: [
      'RELIANCE',
      'TCS',
      'INFY',
      'SBIN',
      'ITC',
      'HDFCBANK',
      'ICICIBANK',
      'LT',
      'AXISBANK',
      'BAJFINANCE',
      'ADANIENT',
      'WIPRO',
      'MARUTI',
      'TITAN',
      'ASIANPAINT'
    ],
    Commodities: [
      'GOLD',
      'SILVER',
      'CRUDEOIL',
      'NATURALGAS',
      'COPPER'
    ],
    Currency: [
      'USDINR',
      'EURINR',
      'GBPINR',
      'JPYINR'
    ]
  },

  Forex: {
    Forex: [
      'EURUSD',
      'GBPUSD',
      'USDJPY',
      'USDCHF',
      'AUDUSD',
      'NZDUSD',
      'USDCAD',
      'EURGBP',
      'EURJPY',
      'GBPJPY'
    ],

    Crypto: [
      'BTCUSDT',
      'ETHUSDT',
      'SOLUSDT',
      'XRPUSDT',
      'DOGEUSDT',
      'BNBUSDT',
      'ADAUSDT',
      'AVAXUSDT',
      'LTCUSDT'
    ],

    Indices: [
      'NAS100',
      'US30',
      'SPX500',
      'GER40',
      'UK100'
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
    useState(12540);

  const [connectionData, setConnectionData] =
    useState({
      broker: '',
      apiKey: '',
      clientId: '',
      password: '',
      totp: '',
      accessToken: '',
      server: ''
    });

  useEffect(() => {

    const validateLicense =
      async () => {

        const license =
          localStorage.getItem(
            'clientLicense'
          );

        if (!license) {

          window.location.href = '/';

          return;

        }

        try {

          const response =
            await fetch(
              `${process.env.REACT_APP_API_URL}/api/license/validate`,
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
              'clientLicense'
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

    const savedBroker =
      localStorage.getItem(
        'brokerConnection'
      );

    if (savedBroker) {

      setBrokerConnected(true);

      setConnectionData(
        JSON.parse(savedBroker)
      );

    }

    const timer = setInterval(() => {

      const now = new Date();

      setCurrentTime(
        now.toLocaleTimeString()
      );

    }, 1000);

    const pnlTimer =
      setInterval(() => {

        setRunningPL((prev) => {

          const randomMove =
            Math.floor(
              Math.random() * 1000
            ) - 500;

          return prev + randomMove;

        });

      }, 4000);

    return () => {

      clearInterval(timer);
      clearInterval(pnlTimer);

    };

  }, []);

  const logout = () => {

    localStorage.removeItem(
      'clientLicense'
    );

    window.location.href = '/';

  };

  const connectBroker = () => {

    localStorage.setItem(
      'brokerConnection',
      JSON.stringify(connectionData)
    );

    setBrokerConnected(true);

    alert(
      'Broker Connected Successfully'
    );

  };

  const toggleAlgo = () => {

    setAlgoActive(!algoActive);

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
              Multi-Market AI Trading Terminal
            </p>

          </div>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-6 py-3 rounded-xl"
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
              Market:
            </span>

            <span className="text-blue-400 font-bold ml-2">
              {marketType === 'Indian'
                ? 'NSE/BSE LIVE'
                : 'FOREX LIVE'}
            </span>
          </div>

          <div className="bg-zinc-800 px-4 py-2 rounded-full border border-purple-500">
            <span className="text-zinc-400">
              Mode:
            </span>

            <span className="text-purple-400 font-bold ml-2">
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
                onClick={() => setMarketType('Indian')}
                className={`flex-1 py-4 rounded-2xl text-xl ${marketType === 'Indian' ? 'bg-purple-600' : 'bg-zinc-800'}`}
              >
                Indian Market
              </button>

              <button
                onClick={() => setMarketType('Forex')}
                className={`flex-1 py-4 rounded-2xl text-xl ${marketType === 'Forex' ? 'bg-purple-600' : 'bg-zinc-800'}`}
              >
                Forex / Crypto
              </button>

            </div>

            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(
                  e.target.value
                );
                setSelectedPair('');
              }}
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
                onClick={toggleAlgo}
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

                {marketType === 'Indian' ? (
                  <>
                    <option value="AngelOne">
                      Angel One
                    </option>

                    <option value="Dhan">
                      Dhan
                    </option>
                  </>
                ) : (
                  <>
                    <option value="MT4">
                      MT4
                    </option>

                    <option value="MT5">
                      MT5
                    </option>
                  </>
                )}

              </select>

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

          <div className="bg-zinc-900 border border-yellow-500 rounded-2xl p-6">
            <h3 className="text-zinc-400 mb-3">
              Running Trades
            </h3>

            <p className="text-4xl font-bold text-yellow-400">
              3
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

        <div className="grid grid-cols-3 gap-6 mb-8">

          <div className="bg-zinc-900 border border-green-600 rounded-3xl p-6">

            <h2 className="text-2xl font-bold text-green-400 mb-4">
              Algo Engine
            </h2>

            <div className="space-y-3 text-lg">

              <div className="flex justify-between">
                <span className="text-zinc-400">
                  Status
                </span>

                <span className={`${algoActive ? 'text-green-400' : 'text-red-400'} font-bold`}>
                  {algoActive
                    ? 'RUNNING'
                    : 'STOPPED'}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-zinc-400">
                  Mode
                </span>

                <span className="text-blue-400 font-bold">
                  {watchOnly
                    ? 'WATCH ONLY'
                    : 'AUTO EXECUTION'}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-zinc-400">
                  Broker
                </span>

                <span className="text-purple-400 font-bold">
                  {connectionData.broker || 'Not Connected'}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-zinc-400">
                  Selected Pair
                </span>

                <span className="text-yellow-400 font-bold">
                  {selectedPair || 'AUTO SCAN'}
                </span>
              </div>

            </div>

          </div>

          <div className="bg-zinc-900 border border-yellow-600 rounded-3xl p-6 col-span-2">

            <div className="flex justify-between items-center mb-6">

              <h2 className="text-2xl font-bold text-yellow-400">
                Active Trade Monitor
              </h2>

              <div className="bg-green-600 px-4 py-2 rounded-full text-sm">
                LIVE MONITORING
              </div>

            </div>

            <table className="w-full">

              <thead>

                <tr className="border-b border-zinc-700 text-zinc-400">

                  <th className="text-left p-4">
                    Pair
                  </th>

                  <th className="text-left p-4">
                    Type
                  </th>

                  <th className="text-left p-4">
                    Entry
                  </th>

                  <th className="text-left p-4">
                    SL
                  </th>

                  <th className="text-left p-4">
                    TP
                  </th>

                  <th className="text-left p-4">
                    Status
                  </th>

                  <th className="text-left p-4">
                    P/L
                  </th>

                </tr>

              </thead>

              <tbody>

                <tr className="border-b border-zinc-800">

                  <td className="p-4 text-purple-400 font-bold">
                    {selectedPair || 'NIFTY'}
                  </td>

                  <td className="p-4 text-green-400 font-bold">
                    BUY
                  </td>

                  <td className="p-4">
                    24500
                  </td>

                  <td className="p-4 text-red-400">
                    24380
                  </td>

                  <td className="p-4 text-green-400">
                    24820
                  </td>

                  <td className="p-4">
                    <span className="bg-green-600 px-4 py-2 rounded-full text-sm">
                      RUNNING
                    </span>
                  </td>

                  <td className="p-4 text-green-400 font-bold">
                    +₹3,200
                  </td>

                </tr>

              </tbody>

            </table>

          </div>

        </div>

        <div className="bg-zinc-900 border border-blue-600 rounded-3xl p-8 mt-8">

          <div className="flex justify-between items-center mb-6">

            <h2 className="text-3xl font-bold text-blue-400">
              Live Algo Activity
            </h2>

            <div className="bg-blue-600 px-4 py-2 rounded-full text-sm">
              REAL-TIME ENGINE
            </div>

          </div>

          <div className="space-y-4">

            <div className="flex justify-between items-center bg-zinc-800 p-4 rounded-2xl">

              <div>
                <p className="font-bold text-green-400">
                  NIFTY BUY Executed
                </p>

                <p className="text-zinc-400 text-sm mt-1">
                  Algo entered long position automatically
                </p>
              </div>

              <div className="text-right">
                <p className="text-white font-bold">
                  09:15 AM
                </p>

                <p className="text-green-400 text-sm">
                  SUCCESS
                </p>
              </div>

            </div>

            <div className="flex justify-between items-center bg-zinc-800 p-4 rounded-2xl">

              <div>
                <p className="font-bold text-yellow-400">
                  BTCUSDT Monitoring
                </p>

                <p className="text-zinc-400 text-sm mt-1">
                  Watch-only mode enabled
                </p>
              </div>

              <div className="text-right">
                <p className="text-white font-bold">
                  09:20 AM
                </p>

                <p className="text-yellow-400 text-sm">
                  MONITORING
                </p>
              </div>

            </div>

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