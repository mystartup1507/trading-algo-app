global.WebSocket = require('ws');
require('dotenv').config();

const express =
  require('express');

const cors =
  require('cors');

const jwt =
  require('jsonwebtoken');

const bcrypt =
  require('bcryptjs');

const {
  createClient
} = require('@supabase/supabase-js');

const {
  connectAngelBroker,
  placeOrder
} = require('./services/angelService');

const app =
  express();

app.use(cors());

app.use(express.json());

const PORT =
  process.env.PORT || 5000;

const supabase =
  createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

const ADMIN_EMAIL =
  process.env.ADMIN_EMAIL;

const ADMIN_PASSWORD =
  process.env.ADMIN_PASSWORD;

const JWT_SECRET =
  process.env.JWT_SECRET;

const verifyAdmin =
  (req, res, next) => {

    try {

      const authHeader =
        req.headers.authorization;

      if (!authHeader) {

        return res.status(401).json({
          success: false,
          message:
            'Unauthorized'
        });

      }

      const token =
        authHeader.split(' ')[1];

      const decoded =
        jwt.verify(
          token,
          JWT_SECRET
        );

      req.admin = decoded;

      next();

    } catch (error) {

      return res.status(401).json({
        success: false,
        message:
          'Invalid Token'
      });

    }

};

app.get(
  '/',
  (req, res) => {

    res.json({
      success: true,
      message:
        'JD-Algo Backend Running'
    });

  }
);

app.post(
  '/api/admin/login',
  async (req, res) => {

    try {

      const {
        email,
        password
      } = req.body;

      if (
        email !== ADMIN_EMAIL
      ) {

        return res.status(401).json({
          success: false,
          message:
            'Invalid Credentials'
        });

      }

      const isMatch =
        await bcrypt.compare(
          password,
          ADMIN_PASSWORD
        );

      if (!isMatch) {

        return res.status(401).json({
          success: false,
          message:
            'Invalid Credentials'
        });

      }

      const token =
        jwt.sign(
          { email },
          JWT_SECRET,
          { expiresIn: '7d' }
        );

      res.json({
        success: true,
        token
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.post(
  '/api/license/create',
  verifyAdmin,
  async (req, res) => {

    try {

      const {
        license_key,
        user_email,
        expires_at,
        plan
      } = req.body;

      const {
        data,
        error
      } = await supabase
        .from('licenses')
        .insert([
          {
            license_key,
            user_email,
            expires_at,
            plan,
            is_active: true,
            status: 'active'
          }
        ]);

      if (error) {

        return res.status(400).json({
          success: false,
          message:
            error.message
        });

      }

      res.json({
        success: true,
        data
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.post(
  '/api/license/validate',
  async (req, res) => {

    try {

      const {
        licenseKey
      } = req.body;

      const {
        data,
        error
      } = await supabase
        .from('licenses')
        .select('*')
        .eq(
          'license_key',
          licenseKey.trim()
        )
        .single();

      if (
        error ||
        !data
      ) {

        return res.status(404).json({
          success: false,
          message:
            'Invalid License'
        });

      }

      if (
        data.is_active === false
      ) {

        return res.status(403).json({
          success: false,
          message:
            'License Revoked'
        });

      }

      if (
        data.expires_at
      ) {

        const currentDate =
          new Date();

        const expiryDate =
          new Date(
            data.expires_at
          );

        if (
          expiryDate < currentDate
        ) {

          return res.status(403).json({
            success: false,
            message:
              'License Expired'
          });

        }

      }

      res.json({
        success: true,
        data
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.get(
  '/api/admin/licenses',
  verifyAdmin,
  async (req, res) => {

    try {

      const {
        data,
        error
      } = await supabase
        .from('licenses')
        .select('*')
        .order(
          'created_at',
          { ascending: false }
        );

      if (error) {

        return res.status(400).json({
          success: false,
          message:
            error.message
        });

      }

      res.json({
        success: true,
        data
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.put(
  '/api/license/revoke/:id',
  verifyAdmin,
  async (req, res) => {

    try {

      const {
        id
      } = req.params;

      const {
        data,
        error
      } = await supabase
        .from('licenses')
        .update({
          is_active: false,
          status: 'revoked'
        })
        .eq('id', id);

      if (error) {

        return res.status(400).json({
          success: false,
          message:
            error.message
        });

      }

      res.json({
        success: true,
        data
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.post(
  '/api/broker/order/angel',
  async (req, res) => {

    try {

      const result =
        await placeOrder(
          req.body
        );

      if (!result.success) {

        return res.status(400).json({
          success: false,
          message:
            result.message
        });

      }

      res.json({
        success: true,
        data:
          result.data
      });

    } catch (error) {

      res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.post(
  '/api/broker/connect',
  async (req, res) => {

    try {

      const {
        broker,
        clientId,
        password,
        totp
      } = req.body;

      if (
        broker !== 'angel'
      ) {

        return res.status(400).json({
          success: false,
          message: 'Only Angel supported currently'
        });

      }

      const result =
        await connectAngelBroker({
          apiKey:
            process.env.ANGEL_API_KEY,
          clientId,
          password,
          totp
        });

      if (!result.success) {

        return res.status(400).json({
          success: false,
          message: result.message
        });

      }

      return res.json({
        success: true,
        message:
          'Broker Connected',
        data: result.data
      });

    } catch (error) {

      return res.status(500).json({
        success: false,
        message:
          error.message
      });

    }

  }
);

app.listen(
  PORT,
  () => {

    console.log(
      `Server running on port ${PORT}`
    );

  }
);
