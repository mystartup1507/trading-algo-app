import React from 'react';

import {
  Activity,
  Wifi,
  ShieldCheck,
  Server,
  PlugZap
} from 'lucide-react';

const StatusCards = ({
  brokerConnected,
  algoRunning
}) => {

  return (

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">

      <div className="bg-zinc-900 border border-green-500/40 rounded-3xl p-6">

        <div className="flex justify-between items-center mb-4">
          <h3 className="text-zinc-400 text-sm">
            Broker
          </h3>

          <PlugZap className="text-green-400" />
        </div>

        <p className={
          brokerConnected
            ? 'text-2xl font-bold text-green-400'
            : 'text-2xl font-bold text-red-400'
        }>
          {
            brokerConnected
              ? 'CONNECTED'
              : 'DISCONNECTED'
          }
        </p>

      </div>

      <div className="bg-zinc-900 border border-purple-500/40 rounded-3xl p-6">

        <div className="flex justify-between items-center mb-4">
          <h3 className="text-zinc-400 text-sm">
            Algo Engine
          </h3>

          <Activity className="text-purple-400" />
        </div>

        <p className={
          algoRunning
            ? 'text-2xl font-bold text-green-400'
            : 'text-2xl font-bold text-red-400'
        }>
          {
            algoRunning
              ? 'RUNNING'
              : 'STOPPED'
          }
        </p>

      </div>

      <div className="bg-zinc-900 border border-yellow-500/40 rounded-3xl p-6">

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

      <div className="bg-zinc-900 border border-blue-500/40 rounded-3xl p-6">

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

      <div className="bg-zinc-900 border border-red-500/40 rounded-3xl p-6">

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

  );

};

export default StatusCards;