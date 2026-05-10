import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import LicenseManager from '../components/LicenseManager';

export default function AdminDashboard() {

  const navigate = useNavigate();

  const [licenses, setLicenses] = useState([]);
  const [loading, setLoading] = useState(true);

  const adminData = JSON.parse(
    localStorage.getItem('adminData')
  );

  useEffect(() => {

    const fetchLicenses = async () => {

      try {

        const token = localStorage.getItem('adminToken');

        const response = await fetch(
          'https://trading-algo-app.onrender.com/api/admin/licenses',
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await response.json();

        if (data.success) {

          setLicenses(data.licenses);

        }

      } catch (error) {

        console.error(error);

      } finally {

        setLoading(false);

      }

    };

    fetchLicenses();

  }, []);

  const logout = () => {

    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminData');

    navigate('/admin-login');

  };

  return (

    <div className="min-h-screen bg-black text-white flex">

      {/* Sidebar */}

      <div className="w-[250px] bg-zinc-900 p-6 border-r border-purple-500">

        <h1 className="text-3xl font-bold mb-10 text-purple-400">
          JD-Algo
        </h1>

        <div className="space-y-4">

          <button className="w-full bg-purple-600 p-3 rounded-xl">
            Dashboard
          </button>

          <button className="w-full bg-zinc-800 p-3 rounded-xl">
            Licenses
          </button>

          <button className="w-full bg-zinc-800 p-3 rounded-xl">
            Users
          </button>

          <button className="w-full bg-zinc-800 p-3 rounded-xl">
            Brokers
          </button>

        </div>

      </div>

      {/* Main Content */}

      <div className="flex-1 p-10">

        <div className="flex justify-between items-center mb-10">

          <div>

            <h1 className="text-4xl font-bold">
              Welcome Admin
            </h1>

            <p className="text-zinc-400 mt-2">
              {adminData?.email}
            </p>

          </div>

          <button
            onClick={logout}
            className="bg-red-600 px-6 py-3 rounded-xl"
          >
            Logout
          </button>

        </div>

        {/* Stats */}

        <div className="grid grid-cols-3 gap-6 mb-10">

          <div className="bg-zinc-900 p-6 rounded-2xl border border-purple-500">

            <h2 className="text-xl font-bold mb-3">
              Total Licenses
            </h2>

            <p className="text-5xl font-bold text-purple-400">

              {loading
                ? '...'
                : licenses.length}

            </p>

          </div>

          <div className="bg-zinc-900 p-6 rounded-2xl border border-purple-500">

            <h2 className="text-xl font-bold mb-3">
              Active Licenses
            </h2>

            <p className="text-5xl font-bold text-green-400">

              {loading
                ? '...'
                : licenses.filter(
                    lic => lic.is_active === true
                  ).length}

            </p>

          </div>

          <div className="bg-zinc-900 p-6 rounded-2xl border border-purple-500">

            <h2 className="text-xl font-bold mb-3">
              Revenue
            </h2>

            <p className="text-5xl font-bold text-yellow-400">
              ₹
              {
                loading
                  ? '...'
                  : licenses.length * 2999
              }
            </p>

          </div>

        </div>

        {/* License Management */}

        <LicenseManager />

      </div>

    </div>

  );

}