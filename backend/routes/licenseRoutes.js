const express = require('express');

const router = express.Router();

const supabase = require('../config/supabase');

router.post(
  '/validate',
  async (req, res) => {

    try {

      const { licenseKey } =
        req.body;

      const { data, error } =
        await supabase
          .from('licenses')
          .select('*')
          .eq(
            'license_key',
            licenseKey
          )
          .single();

      if (error || !data) {

        return res.status(401).json({
          success: false,
          message:
            'Invalid License Key'
        });

      }

      if (!data.is_active) {

        return res.status(401).json({
          success: false,
          message:
            'License Revoked'
        });

      }

      if (
        new Date(data.expires_at) <
        new Date()
      ) {

        return res.status(401).json({
          success: false,
          message:
            'License Expired'
        });

      }

      return res.status(200).json({
        success: true
      });

    } catch (error) {

      return res.status(500).json({
        success: false,
        message:
          'Server Error'
      });

    }

  }
);

module.exports = router;