const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

const supabase = require('../config/supabase');

const loginAdmin = async (req, res) => {
  try {
    const { email, password } = req.body;

    const { data: admin, error } = await supabase
      .from('admins')
      .select('*')
      .eq('email', email)
      .eq('password', password)
      .single();

    if (error || !admin) {
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    const token = jwt.sign(
      {
        id: admin.id,
        email: admin.email
      },
      process.env.JWT_SECRET,
      {
        expiresIn: '7d'
      }
    );

    return res.status(200).json({
      success: true,
      token
    });

  } catch (error) {

    console.log(error);

    return res.status(500).json({
      success: false,
      message: error.message
    });

  }
};

const generateLicense = async (req, res) => {

  try {

    const {
      userEmail,
      plan,
      expiresAt
    } = req.body;

    const licenseKey =
      'JD-' +
      uuidv4()
        .split('-')[0]
        .toUpperCase();

    const { data, error } = await supabase
      .from('licenses')
      .insert([
        {
          user_email: userEmail,
          license_key: licenseKey,
          plan: plan,
          expires_at: expiresAt,
          is_active: true,
          status: 'active'
        }
      ])
      .select();

    console.log('GENERATE LICENSE:', data);
    console.log('GENERATE ERROR:', error);

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    return res.status(200).json({
      success: true,
      license: data[0]
    });

  } catch (error) {

    console.log(error);

    return res.status(500).json({
      success: false,
      message: error.message
    });

  }
};

const getAllLicenses = async (req, res) => {

  try {

    const { data, error } = await supabase
      .from('licenses')
      .select('*')
      .order('created_at', {
        ascending: false
      });

    console.log('LICENSE DATA:', data);
    console.log('LICENSE ERROR:', error);

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    return res.status(200).json({
      success: true,
      licenses: data
    });

  } catch (error) {

    console.log(error);

    return res.status(500).json({
      success: false,
      message: error.message
    });

  }
};

const revokeLicense = async (req, res) => {

  try {

    const { id } = req.params;

    const { data, error } = await supabase
      .from('licenses')
      .update({
        is_active: false,
        status: 'revoked'
      })
      .eq('id', id)
      .select();

    console.log('REVOKE DATA:', data);
    console.log('REVOKE ERROR:', error);

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    return res.status(200).json({
      success: true,
      message: 'License revoked'
    });

  } catch (error) {

    console.log(error);

    return res.status(500).json({
      success: false,
      message: error.message
    });

  }
};

const getDashboardStats = async (req, res) => {

  try {

    const { data: licenses, error } =
      await supabase
        .from('licenses')
        .select('*');

    console.log('STATS LICENSES:', licenses);
    console.log('STATS ERROR:', error);

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    const totalLicenses =
      licenses.length;

    const activeLicenses =
      licenses.filter(
        (item) => item.is_active === true
      ).length;

    const expiredLicenses =
      licenses.filter((item) => {

        if (!item.expires_at)
          return false;

        return (
          new Date(item.expires_at) <
          new Date()
        );

      }).length;

    return res.status(200).json({
      success: true,
      stats: {
        totalLicenses,
        activeLicenses,
        expiredLicenses
      }
    });

  } catch (error) {

    console.log(error);

    return res.status(500).json({
      success: false,
      message: error.message
    });

  }
};

module.exports = {
  loginAdmin,
  generateLicense,
  getAllLicenses,
  revokeLicense,
  getDashboardStats
};