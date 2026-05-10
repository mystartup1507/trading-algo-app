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
        email: admin.email,
        role: admin.role
      },
      process.env.JWT_SECRET,
      {
        expiresIn: '7d'
      }
    );

    return res.status(200).json({
      success: true,
      token,
      admin: {
        id: admin.id,
        email: admin.email,
        role: admin.role
      }
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

const generateLicense = async (req, res) => {
  try {
    const { userEmail, plan, expiresAt } = req.body;

    const licenseKey =
      'JD-ALGO-' +
      uuidv4().split('-')[0].toUpperCase();

    const { data, error } = await supabase
      .from('licenses')
      .insert([
        {
          license_key: licenseKey,
          user_email: userEmail,
          plan,
          expires_at: expiresAt,
          is_active: true,
          status: 'active',
          max_devices: 1
        }
      ])
      .select();

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    return res.status(200).json({
      success: true,
      message: 'License created successfully',
      license: data[0]
    });
  } catch (error) {
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
    return res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

const getDashboardStats = async (req, res) => {
  try {
    const { data: licenses, error } = await supabase
      .from('licenses')
      .select('*');

    if (error) {
      return res.status(500).json({
        success: false,
        message: error.message
      });
    }

    const totalLicenses = licenses.length;

    const activeLicenses = licenses.filter(
      (item) => item.is_active === true
    ).length;

    const expiredLicenses = licenses.filter(
      (item) => {
        if (!item.expires_at) return false;

        return (
          new Date(item.expires_at) <
          new Date()
        );
      }
    ).length;

    return res.status(200).json({
      success: true,
      stats: {
        totalLicenses,
        activeLicenses,
        expiredLicenses
      }
    });
  } catch (error) {
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
  getDashboardStats
};