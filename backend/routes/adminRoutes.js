const express = require('express');

const router = express.Router();

const verifyAdmin = require('../middleware/authMiddleware');

const {
  createLicense,
  getAllLicenses
} = require('../controllers/adminController');

router.post(
  '/generate-license',
  verifyAdmin,
  createLicense
);
router.get(
  '/licenses',
  verifyAdmin,
  getAllLicenses
);

module.exports = router;