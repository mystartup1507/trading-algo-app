
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import AdminLogin from './pages/AdminLogin';
import AdminDashboard from './pages/AdminDashboard';

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Navigate to="/admin-login" />} />

        <Route
          path="/admin-login"
          element={<AdminLogin />}
        />

        <Route
  path="/admin-dashboard"
  element={<AdminDashboard />}
/>  
     

      </Routes>

    </BrowserRouter>

  );

}

export default App;