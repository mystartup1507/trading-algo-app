import React from 'react';
import { LogOut } from 'lucide-react';

const Header = () => {

const logout = () => {

  localStorage.clear();

  window.location.href = '/';

};
  return (

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

  );

};

export default Header;