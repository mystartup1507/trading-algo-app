import React, {
  useEffect,
  useState
} from 'react';

import Header from '../components/Header';
import StatusCards from '../components/StatusCards';
import MarketSelector from '../components/MarketSelector';
import BrokerPanel from '../components/BrokerPanel';
import StatsCards from '../components/StatsCards';
import AIEngineStatus from '../components/AIEngineStatus';

const ClientDashboard = () => {

  const [brokerConnected, setBrokerConnected] =
    useState(false);

  const [currentTime, setCurrentTime] =
    useState('');

  const [runningPL] =
    useState(0);

  const [availableBalance, setAvailableBalance] =
    useState(0);

  const [runningTrades, setRunningTrades] =
    useState(0);

  const [positions, setPositions] =
    useState([]);

  const [selectedMarket, setSelectedMarket] =
    useState('indian');

  const [selectedBroker, setSelectedBroker] =
    useState('angel');

  const [tradingMode, setTradingMode] =
    useState('auto');

  const [selectedPair, setSelectedPair] =
    useState('');

  const [algoRunning, setAlgoRunning] =
    useState(false);

  const [connectionData, setConnectionData] =
    useState({
      clientId: '',
      password: '',
      totp: '',
      server: ''
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

    const timer = setInterval(() => {

      setCurrentTime(
        new Date().toLocaleTimeString()
      );

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

  const connectBroker = async () => {

    try {

      if (
        !connectionData.clientId ||
        !connectionData.password
      ) {

        alert(
          'Please fill broker credentials'
        );

        return;

      }

      const response =
        await fetch(
          'https://jdalgoapi.duckdns.org/api/broker/connect',
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json'
            },

            body: JSON.stringify({

              apiKey:
                'QTgnsVLk',

              broker:
                selectedBroker,

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

        alert(data.message);
        return;

      }

      localStorage.setItem(
        'brokerConnection',
        'true'
      );

      setBrokerConnected(true);

      const profileResponse =
        await fetch(
          'https://jdalgoapi.duckdns.org/api/broker/profile',
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

      const profileData =
        await profileResponse.json();

      if (profileData.success) {

      setAvailableBalance(
          profileData.rms?.data?.availablecash || 0
        );

      }

      setPositions([]);
setRunningTrades(0);

      alert(
        'Broker Connected Successfully'
      );

    } catch (error) {

      console.log(error);

      alert(
        'Connection Error'
      );

    }

  };

  const disconnectBroker = () => {

    localStorage.removeItem(
      'brokerConnection'
    );

    setBrokerConnected(false);

    setPositions([]);

    alert(
      'Broker Disconnected'
    );

  };

  const toggleAlgo = async () => {

    try {

      if (!brokerConnected) {

        alert(
          'Connect Broker First'
        );

        return;

      }

      if (algoRunning) {

        setAlgoRunning(false);

        alert(
          'Algo Stopped'
        );

        return;

      }

const response =
  await fetch(
    'https://jdalgoapi.duckdns.org/api/algo/start',
    {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify({

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

        alert(data.message);
        return;

      }

      setAlgoRunning(true);

      alert(
        'AI Engine Started'
      );

    } catch (error) {

      alert(
        'Order Execution Failed'
      );

    }

  };

  return (

    <div className="min-h-screen bg-black text-white">

      <Header />

      <main className="p-8 space-y-8">

        <StatusCards
          brokerConnected={brokerConnected}
          algoRunning={algoRunning}
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

          <MarketSelector
            selectedMarket={selectedMarket}
            setSelectedMarket={setSelectedMarket}
            selectedBroker={selectedBroker}
            setSelectedBroker={setSelectedBroker}
            tradingMode={tradingMode}
            setTradingMode={setTradingMode}
            selectedPair={selectedPair}
            setSelectedPair={setSelectedPair}
          />

          <BrokerPanel
            selectedMarket={selectedMarket}
            connectionData={connectionData}
            setConnectionData={setConnectionData}
            brokerConnected={brokerConnected}
            connectBroker={connectBroker}
            disconnectBroker={disconnectBroker}
            algoRunning={algoRunning}
            toggleAlgo={toggleAlgo}
          />

        </div>

        <AIEngineStatus />

        <div className="bg-zinc-950 border border-cyan-500/20 rounded-2xl p-6">

          <h2 className="text-2xl font-bold mb-6 text-cyan-400">
            Live Positions
          </h2>

          {
            positions.length === 0 ? (

              <div className="text-zinc-400">
                No Active Positions
              </div>

            ) : (

              positions.map((trade, index) => (

                <div
                  key={index}
                  className="bg-zinc-900 p-4 rounded-xl mb-3"
                >

                  <div className="flex justify-between">

                    <span>
                      {trade.tradingsymbol}
                    </span>

                    <span>
                      Qty:
                      {' '}
                      {trade.netqty}
                    </span>

                  </div>

                  <div className="flex justify-between mt-2">

                    <span>
                      Avg:
                      {' '}
                      ₹
                      {trade.averageprice}
                    </span>

                    <span>
                      P/L:
                      {' '}
                      ₹
                      {trade.pnl}
                    </span>

                  </div>

                </div>

              ))

            )
          }

        </div>

        <StatsCards
          runningPL={runningPL}
          availableBalance={availableBalance}
          runningTrades={runningTrades}
          currentTime={currentTime}
        />

      </main>

    </div>

  );

};

export default ClientDashboard;
