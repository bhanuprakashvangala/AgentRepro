const jwt = require('jsonwebtoken');
require('dotenv').config();

class JWTAuthService {
  constructor() {
    this.secret = process.env.JWT_SECRET || 'your-secret-key-change-this';
    this.expiresIn = process.env.JWT_EXPIRES_IN || '1h';
    this.refreshExpiresIn = process.env.JWT_REFRESH_EXPIRES_IN || '7d';
  }

  /**
   * Generate access token
   */
  generateToken(payload) {
    try {
      return jwt.sign(payload, this.secret, { expiresIn: this.expiresIn });
    } catch (error) {
      throw new Error(`Token generation failed: ${error.message}`);
    }
  }

  /**
   * Generate refresh token
   */
  generateRefreshToken(payload) {
    try {
      return jwt.sign(payload, this.secret, { expiresIn: this.refreshExpiresIn });
    } catch (error) {
      throw new Error(`Refresh token generation failed: ${error.message}`);
    }
  }

  /**
   * Verify token
   */
  verifyToken(token) {
    try {
      return jwt.verify(token, this.secret);
    } catch (error) {
      if (error.name === 'TokenExpiredError') {
        throw new Error('Token expired');
      } else if (error.name === 'JsonWebTokenError') {
        throw new Error('Invalid token');
      }
      throw error;
    }
  }

  /**
   * Decode token without verification (for debugging)
   */
  decodeToken(token) {
    return jwt.decode(token);
  }

  /**
   * Express middleware for authentication
   */
  authenticateToken() {
    return (req, res, next) => {
      const authHeader = req.headers['authorization'];
      const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

      if (!token) {
        return res.status(401).json({ error: 'Access token required' });
      }

      try {
        const decoded = this.verifyToken(token);
        req.user = decoded;
        next();
      } catch (error) {
        return res.status(403).json({ error: error.message });
      }
    };
  }

  /**
   * Optional: Role-based middleware
   */
  requireRole(roles) {
    return (req, res, next) => {
      if (!req.user) {
        return res.status(401).json({ error: 'Authentication required' });
      }

      const userRoles = Array.isArray(req.user.role) ? req.user.role : [req.user.role];
      const requiredRoles = Array.isArray(roles) ? roles : [roles];

      const hasRole = requiredRoles.some(role => userRoles.includes(role));

      if (!hasRole) {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }

      next();
    };
  }
}

module.exports = JWTAuthService;

// Example server implementation
if (require.main === module) {
  const express = require('express');
  const app = express();
  app.use(express.json());

  const authService = new JWTAuthService();

  // Mock user database
  const users = [
    { id: 1, email: 'admin@example.com', password: 'admin123', role: 'admin' },
    { id: 2, email: 'user@example.com', password: 'user123', role: 'user' }
  ];

  // Login endpoint
  app.post('/login', (req, res) => {
    const { email, password } = req.body;

    const user = users.find(u => u.email === email && u.password === password);

    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = authService.generateToken({
      userId: user.id,
      email: user.email,
      role: user.role
    });

    const refreshToken = authService.generateRefreshToken({ userId: user.id });

    res.json({
      success: true,
      token,
      refreshToken,
      user: { id: user.id, email: user.email, role: user.role }
    });
  });

  // Protected endpoint
  app.get('/protected', authService.authenticateToken(), (req, res) => {
    res.json({
      message: 'This is protected data',
      user: req.user
    });
  });

  // Admin only endpoint
  app.get('/admin', authService.authenticateToken(), authService.requireRole('admin'), (req, res) => {
    res.json({
      message: 'Admin data',
      user: req.user
    });
  });

  // Refresh token endpoint
  app.post('/refresh', (req, res) => {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(401).json({ error: 'Refresh token required' });
    }

    try {
      const decoded = authService.verifyToken(refreshToken);
      const newToken = authService.generateToken({
        userId: decoded.userId
      });

      res.json({ success: true, token: newToken });
    } catch (error) {
      res.status(403).json({ error: error.message });
    }
  });

  const PORT = 3000;
  app.listen(PORT, () => {
    console.log(`JWT Auth server running on port ${PORT}`);
    console.log('\nEndpoints:');
    console.log('  POST /login - Get JWT token');
    console.log('  GET /protected - Protected endpoint (requires token)');
    console.log('  GET /admin - Admin only endpoint');
    console.log('  POST /refresh - Refresh access token');
  });
}
