import {
  BrowserRouter,
  Routes,
  Route
} from 'react-router-dom';

import ClientActivation
from './pages/ClientActivation';

import ClientDashboard
from './pages/ClientDashboard';

function App() {

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={
            <ClientActivation />
          }
        />

        <Route
          path="/dashboard"
          element={
            <ClientDashboard />
          }
        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;