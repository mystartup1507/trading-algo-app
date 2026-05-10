import { useEffect, useState } from 'react';
import axios from 'axios';

export default function LicenseManager() {

  const [licenses, setLicenses] = useState([]);

  const [formData, setFormData] = useState({
    userEmail: '',
    plan: 'premium',
    expiresAt: ''
  });

  const token = localStorage.getItem('adminToken');

  const fetchLicenses = async () => {

    try {

      const res = await axios.get(
        'http://localhost:5000/api/admin/licenses',
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setLicenses(res.data.licenses);

    } catch (err) {

      console.error(err);

    }

  };

  useEffect(() => {

    fetchLicenses();

  }, []);

  const generateLicense = async (e) => {

    e.preventDefault();

    try {

      await axios.post(
        'http://localhost:5000/api/admin/generate-license',
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      alert('License Generated');

      fetchLicenses();

    } catch (err) {

      alert(
        err.response?.data?.message ||
        'Error generating license'
      );

    }

  };

  return (

    <div className="mt-10">

      <div className="bg-zinc-900 p-6 rounded-2xl border border-purple-500 mb-10">

        <h2 className="text-2xl font-bold mb-6">
          Generate License
        </h2>

        <form
          onSubmit={generateLicense}
          className="grid grid-cols-3 gap-4"
        >

          <input
            type="email"
            placeholder="Client Email"
            className="p-4 rounded-xl bg-zinc-800"
            onChange={(e) =>
              setFormData({
                ...formData,
                userEmail: e.target.value
              })
            }
          />

          <select
            className="p-4 rounded-xl bg-zinc-800"
            onChange={(e) =>
              setFormData({
                ...formData,
                plan: e.target.value
              })
            }
          >

            <option value="premium">
              Premium
            </option>

            <option value="trial">
              Trial
            </option>

          </select>

          <input
            type="date"
            className="p-4 rounded-xl bg-zinc-800"
            onChange={(e) =>
              setFormData({
                ...formData,
                expiresAt: e.target.value
              })
            }
          />

          <button
            className="bg-purple-600 p-4 rounded-xl col-span-3"
          >
            Generate License
          </button>

        </form>

      </div>

      <div className="bg-zinc-900 p-6 rounded-2xl border border-purple-500">

        <h2 className="text-2xl font-bold mb-6">
          All Licenses
        </h2>

        <div className="overflow-auto">

          <table className="w-full">

            <thead>

              <tr className="border-b border-zinc-700">

                <th className="text-left p-4">
                  Email
                </th>

                <th className="text-left p-4">
                  License Key
                </th>

                <th className="text-left p-4">
                  Plan
                </th>

                <th className="text-left p-4">
                  Status
                </th>

              </tr>

            </thead>

            <tbody>

              {licenses.map((license) => (

                <tr
                  key={license.id}
                  className="border-b border-zinc-800"
                >

                  <td className="p-4">
                    {license.user_email}
                  </td>

                  <td className="p-4">
                    {license.license_key}
                  </td>

                  <td className="p-4">
                    {license.plan}
                  </td>

                  <td className="p-4">

                    <span className="bg-green-600 px-3 py-1 rounded-full text-sm">
                      {license.status}
                    </span>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

    </div>

  );

}