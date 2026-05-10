require('dotenv').config();

const express = require('express');
const cors = require('cors');

const adminRoutes =
  require('./routes/adminRoutes');

const licenseRoutes =
  require('./routes/licenseRoutes');

const app = express();

app.use(cors());

app.use(express.json());

app.use(
  '/api/auth',
  adminRoutes
);

app.use(
  '/api/admin',
  adminRoutes
);

app.use(
  '/api/license',
  licenseRoutes
);

app.get('/', (req, res) => {

  res.send(
    'JD-Algo Backend Running'
  );

});

const PORT =
  process.env.PORT || 5000;

app.listen(PORT, () => {

  console.log(
    `Server running on port ${PORT}`
  );

});