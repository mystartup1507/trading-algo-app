const express = require('express');

const router = express.Router();

const {
  loginAdmin,
  generateLicense,
  getAllLicenses,
  revokeLicense,
  getDashboardStats
} = require('../controllers/adminController');

const verifyAdminToken = require('../middleware/authMiddleware');

router.post('/login', loginAdmin);

router.post(
  '/generate-license',
  verifyAdminToken,
  generateLicense
);

router.get(
  '/licenses',
  verifyAdminToken,
  getAllLicenses
);

router.put(
  '/revoke-license/:id',
  verifyAdminToken,
  revokeLicense
);

router.get(
  '/dashboard-stats',
  verifyAdminToken,
  getDashboardStats
);

module.exports = router;