import React, {
  useEffect,
  useState
} from 'react';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalLicenses: 0,
    activeLicenses: 0,
    expiredLicenses: 0
  });

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const token =
        localStorage.getItem('adminToken');

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/admin/dashboard-stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      const data = await response.json();

      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.log(error);
    }
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminData');

    window.location.href = '/admin-login';
  };

  return (
    <div className="min-h-screen bg-black text-white flex">
      <div className="w-72 bg-zinc-900 border-r border-purple-600 p-6">
        <h1 className="text-5xl font-bold text-purple-400 mb-10">
          JD-Algo
        </h1>

        <div className="space-y-4">
          <button className="w-full bg-purple-600 py-4 rounded-xl text-xl">
            Dashboard
          </button>

          <button className="w-full bg-zinc-800 py-4 rounded-xl text-xl">
            Licenses
          </button>

          <button className="w-full bg-zinc-800 py-4 rounded-xl text-xl">
            Users
          </button>
        </div>
      </div>

      <div className="flex-1 p-10">
        <div className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-6xl font-bold">
              Welcome Admin
            </h1>

            <p className="text-zinc-400 mt-3 text-xl">
              Live License Management System
            </p>
          </div>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-8 py-4 rounded-xl text-xl"
          >
            Logout
          </button>
        </div>

        <div className="grid grid-cols-3 gap-8">
          <div className="bg-zinc-900 border border-purple-600 rounded-2xl p-8">
            <h2 className="text-3xl font-bold mb-6">
              Total Licenses
            </h2>

            <p className="text-6xl font-bold text-purple-400">
              {stats.totalLicenses}
            </p>
          </div>

          <div className="bg-zinc-900 border border-green-600 rounded-2xl p-8">
            <h2 className="text-3xl font-bold mb-6">
              Active Licenses
            </h2>

            <p className="text-6xl font-bold text-green-400">
              {stats.activeLicenses}
            </p>
          </div>

          <div className="bg-zinc-900 border border-red-600 rounded-2xl p-8">
            <h2 className="text-3xl font-bold mb-6">
              Expired Licenses
            </h2>

            <p className="text-6xl font-bold text-red-400">
              {stats.expiredLicenses}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;