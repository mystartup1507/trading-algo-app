const express = require('express');
const router = express.Router();

const {
  activateLicense
} = require('../controllers/licenseController');

router.post('/activate-license', activateLicense);

module.exports = router;