import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function AdminLogin() {

  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {

    e.preventDefault();

    try {

      const res = await axios.post(
        'https://trading-algo-app.onrender.com/api/auth/login',
        {
          email,
          password
        }
      );

      localStorage.setItem(
        'adminToken',
        res.data.token
      );

      localStorage.setItem(
        'adminData',
        JSON.stringify(res.data.admin)
      );

      alert('Login Successful');

      navigate('/admin-dashboard');

    } catch (err) {

      alert(
        err.response?.data?.message ||
        'Login failed'
      );

    }

  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">

      <form
        onSubmit={handleLogin}
        className="bg-zinc-900 p-10 rounded-2xl w-[400px] border border-purple-500"
      >

        <h1 className="text-4xl font-bold text-white mb-8 text-center">
          JD-Algo Admin
        </h1>

        <input
          type="email"
          placeholder="Admin Email"
          className="w-full p-4 rounded-xl bg-zinc-800 text-white mb-4"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full p-4 rounded-xl bg-zinc-800 text-white mb-6"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          className="w-full p-4 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold"
        >
          Login
        </button>

      </form>

    </div>
  );

}