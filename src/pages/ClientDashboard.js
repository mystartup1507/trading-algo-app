import React, {
  useEffect
} from 'react';

const ClientDashboard = () => {

  useEffect(() => {

    const license =
      localStorage.getItem(
        'clientLicense'
      );

    if (!license) {

      window.location.href = '/';

    }

  }, []);

  const logout = () => {

    localStorage.removeItem(
      'clientLicense'
    );

    window.location.href = '/';

  };

  return (

    <div className="min-h-screen bg-black text-white p-10">

      <div className="flex justify-between items-center mb-10">

        <div>

          <h1 className="text-5xl font-bold text-purple-400">
            JD-Algo
          </h1>

          <p className="text-zinc-400 mt-2">
            AI Trading Dashboard
          </p>

        </div>

        <button
          onClick={logout}
          className="bg-red-600 px-6 py-3 rounded-xl"
        >
          Logout
        </button>

      </div>

      <div className="grid grid-cols-3 gap-6">

        <div className="bg-zinc-900 p-8 rounded-2xl border border-purple-500">

          <h2 className="text-2xl mb-4">
            Bot Status
          </h2>

          <p className="text-green-400 text-4xl font-bold">
            ACTIVE
          </p>

        </div>

        <div className="bg-zinc-900 p-8 rounded-2xl border border-green-500">

          <h2 className="text-2xl mb-4">
            Strategy
          </h2>

          <p className="text-3xl font-bold">
            Quantum Scalper
          </p>

        </div>

        <div className="bg-zinc-900 p-8 rounded-2xl border border-yellow-500">

          <h2 className="text-2xl mb-4">
            Market
          </h2>

          <p className="text-3xl font-bold">
            LIVE
          </p>

        </div>

      </div>

    </div>

  );

};

export default ClientDashboard;