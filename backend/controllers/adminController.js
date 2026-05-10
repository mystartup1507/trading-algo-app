const supabase = require('../config/supabase');

const generateLicenseKey = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

  let result = 'JD-ALGO-';

  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  result += '-';

  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  return result;
};

const createLicense = async (req, res) => {
  try {
    const {
      userEmail,
      plan,
      expiresAt
    } = req.body;

    const licenseKey = generateLicenseKey();

    const { data, error } = await supabase
      .from('licenses')
      .insert([
        {
          license_key: licenseKey,
          user_email: userEmail,
          plan: plan || 'premium',
          status: 'active',
          is_active: true,
          max_devices: 1,
          expires_at: expiresAt
        }
      ])
      .select();

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    res.json({
      success: true,
      message: 'License created successfully',
      license: data[0]
    });

  } catch (err) {
    console.error(err);

    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
};

const getAllLicenses = async (req, res) => {

  try {

    const { data, error } = await supabase
      .from('licenses')
      .select('*')
      .order('id', { ascending: false });

    if (error) {
      throw error;
    }

    res.json({
      success: true,
      licenses: data
    });

  } catch (err) {

    console.error(err);

    res.status(500).json({
      success: false,
      message: 'Server Error'
    });

  }

};

module.exports = {
  createLicense,
  getAllLicenses
};


