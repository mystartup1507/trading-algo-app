import React, {
  useEffect,
  useState
} from 'react';

import Header from '../components/Header';
import StatusCards from '../components/StatusCards';
import MarketSelector from '../components/MarketSelector';
import BrokerPanel from '../components/BrokerPanel';
import StatsCards from '../components/StatsCards';
import AlgoControls from '../components/AlgoControls';

const ClientDashboard = () => {

  const [brokerConnected, setBrokerConnected] =
    useState(false);

  const [currentTime, setCurrentTime] =
    useState('');

  const [runningPL] =
    useState(0);

  const [availableBalance] =
    useState(0);

  const [runningTrades] =
    useState(0);

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

  const [algoSettings, setAlgoSettings] =
  useState({
    riskPercent: 1,
    lotSize: 0.01,
    stopLoss: 30,
    takeProfit: 60,
    maxTrades: 2,
    tradeDirection: 'both',
    confidenceMode: 'balanced'
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

      setBrokerConnected(true);

      alert(
        'Broker Connected Successfully'
      );

    } catch (error) {

      alert('Connection Error');

    }

  };

  const disconnectBroker = () => {

    localStorage.removeItem(
      'brokerConnection'
    );

    setBrokerConnected(false);

    alert(
      'Broker Disconnected'
    );

  };

  const toggleAlgo = () => {

    if (
      tradingMode === 'manual' &&
      !selectedPair
    ) {

      alert(
        'Please enter pair/symbol'
      );

      return;

    }

    setAlgoRunning(!algoRunning);

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

         <AlgoControls
  algoSettings={algoSettings}
  setAlgoSettings={setAlgoSettings}
/>

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