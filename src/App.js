import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import ClientActivation
from './pages/ClientActivation';

import ClientDashboard
from './pages/ClientDashboard';

function App() {

  const isActivated =
    localStorage.getItem('licenseActivated') === 'true';

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={
            isActivated
              ? <Navigate to="/dashboard" />
              : <ClientActivation />
          }
        />

        <Route
          path="/dashboard"
          element={
            isActivated
              ? <ClientDashboard />
              : <Navigate to="/" />
          }
        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;