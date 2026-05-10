import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const LicenseManager = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const licenseKey = localStorage.getItem('licenseKey');

    if (!licenseKey) {
      navigate('/');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="bg-zinc-900 p-10 rounded-2xl border border-purple-500">
        <h1 className="text-4xl font-bold text-purple-400 mb-4">
          JD-Algo License Manager
        </h1>

        <p className="text-gray-300">
          License verified successfully.
        </p>
      </div>
    </div>
  );
};

export default LicenseManager;