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

  const [licenses, setLicenses] =
    useState([]);

  useEffect(() => {
    fetchDashboardStats();
    fetchLicenses();
  }, []);

  const token =
    localStorage.getItem('adminToken');

  const fetchDashboardStats =
    async () => {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/api/admin/dashboard-stats`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data =
          await response.json();

        if (data.success) {
          setStats(data.stats);
        }
      } catch (error) {
        console.log(error);
      }
    };

  const fetchLicenses =
    async () => {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/api/admin/licenses`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data =
          await response.json();

        if (data.success) {
          setLicenses(data.licenses);
        }
      } catch (error) {
        console.log(error);
      }
    };

  const revokeLicense =
    async (id) => {
      try {
        await fetch(
          `${process.env.REACT_APP_API_URL}/api/admin/revoke-license/${id}`,
          {
            method: 'PUT',
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        fetchDashboardStats();
        fetchLicenses();
      } catch (error) {
        console.log(error);
      }
    };

  const logout = () => {
    localStorage.removeItem(
      'adminToken'
    );

    window.location.href =
      '/admin-login';
  };

  return (
    <div className="min-h-screen bg-black text-white p-10">

      <div className="flex justify-between items-center mb-10">

        <div>
          <h1 className="text-5xl font-bold text-purple-400">
            JD-Algo Admin
          </h1>

          <p className="text-zinc-400 mt-2">
            Live License Management
          </p>
        </div>

        <button
          onClick={logout}
          className="bg-red-600 px-6 py-3 rounded-xl"
        >
          Logout
        </button>

      </div>

      <div className="grid grid-cols-3 gap-6 mb-10">

        <div className="bg-zinc-900 p-8 rounded-2xl border border-purple-500">
          <h2 className="text-2xl mb-4">
            Total Licenses
          </h2>

          <p className="text-5xl font-bold text-purple-400">
            {stats.totalLicenses}
          </p>
        </div>

        <div className="bg-zinc-900 p-8 rounded-2xl border border-green-500">
          <h2 className="text-2xl mb-4">
            Active Licenses
          </h2>

          <p className="text-5xl font-bold text-green-400">
            {stats.activeLicenses}
          </p>
        </div>

        <div className="bg-zinc-900 p-8 rounded-2xl border border-red-500">
          <h2 className="text-2xl mb-4">
            Expired Licenses
          </h2>

          <p className="text-5xl font-bold text-red-400">
            {stats.expiredLicenses}
          </p>
        </div>

      </div>

      <div className="bg-zinc-900 rounded-2xl p-6 border border-purple-500">

        <h2 className="text-3xl font-bold mb-6">
          All Licenses
        </h2>

        <div className="overflow-auto">

          <table className="w-full">

            <thead>

              <tr className="border-b border-zinc-700">

                <th className="p-4 text-left">
                  Email
                </th>

                <th className="p-4 text-left">
                  License Key
                </th>

                <th className="p-4 text-left">
                  Plan
                </th>

                <th className="p-4 text-left">
                  Status
                </th>

                <th className="p-4 text-left">
                  Expires
                </th>

                <th className="p-4 text-left">
                  Action
                </th>

              </tr>

            </thead>

            <tbody>

              {licenses.map((item) => (

                <tr
                  key={item.id}
                  className="border-b border-zinc-800"
                >

                  <td className="p-4">
                    {item.user_email}
                  </td>

                  <td className="p-4">
                    {item.license_key}
                  </td>

                  <td className="p-4">
                    {item.plan}
                  </td>

                  <td className="p-4">

                    <span
                      className={`px-4 py-2 rounded-full text-sm ${
                        item.is_active
                          ? 'bg-green-600'
                          : 'bg-red-600'
                      }`}
                    >
                      {item.status}
                    </span>

                  </td>

                  <td className="p-4">
                    {item.expires_at}
                  </td>

                  <td className="p-4">

                    {item.is_active && (

                      <button
                        onClick={() =>
                          revokeLicense(
                            item.id
                          )
                        }
                        className="bg-red-600 px-4 py-2 rounded-lg"
                      >
                        Revoke
                      </button>

                    )}

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
};

export default AdminDashboard;