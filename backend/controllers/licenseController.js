const supabase = require('../config/supabase');

const activateLicense = async (req, res) => {
  try {
    const { licenseKey, deviceId } = req.body;

    if (!licenseKey || !deviceId) {
      return res.status(400).json({
        success: false,
        message: 'License key and device ID required'
      });
    }

    // Find license
    const { data: license, error } = await supabase
      .from('licenses')
      .select('*')
      .eq('license_key', licenseKey)
      .single();

    if (error || !license) {
      return res.status(404).json({
        success: false,
        message: 'Invalid license key'
      });
    }

    // Check active status
    if (!license.is_active) {
      return res.status(403).json({
        success: false,
        message: 'License inactive'
      });
    }

    // First activation
    if (!license.device_id) {
      const { error: updateError } = await supabase
        .from('licenses')
        .update({ device_id: deviceId })
        .eq('license_key', licenseKey);

      if (updateError) {
        return res.status(500).json({
          success: false,
          message: 'Activation failed'
        });
      }

      return res.json({
        success: true,
        message: 'License activated successfully',
        deviceBound: true
      });
    }

    // Already activated on same device
    if (license.device_id === deviceId) {
      return res.json({
        success: true,
        message: 'License verified',
        deviceBound: true
      });
    }

    // Different device
    return res.status(403).json({
      success: false,
      message: 'License already used on another device'
    });

  } catch (err) {
    console.error(err);

    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

module.exports = {
  activateLicense
};