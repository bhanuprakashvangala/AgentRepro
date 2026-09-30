require('dotenv').config();
const express = require('express');
const { connectRedis } = require('./config/redis');
const {
  globalLimiter,
  strictLimiter,
  apiLimiter,
  heavyOperationLimiter,
  searchLimiter,
  createRateLimiter,
} = require('./middleware/rateLimiter');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Trust proxy - important for getting correct IP addresses behind proxies/load balancers
app.set('trust proxy', 1);

// Apply global rate limiter to all routes
app.use(globalLimiter);

// Health check endpoint (no additional rate limiting)
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Public API endpoints with standard rate limiting
app.get('/api/public/data', apiLimiter, (req, res) => {
  res.json({
    message: 'Public data accessed successfully',
    data: { example: 'data' },
  });
});

// Search endpoint with specific rate limiting
app.get('/api/search', searchLimiter, (req, res) => {
  const { q } = req.query;
  res.json({
    message: 'Search completed',
    query: q,
    results: [],
  });
});

// Authentication endpoints with strict rate limiting
app.post('/api/auth/login', strictLimiter, (req, res) => {
  const { username, password } = req.body;

  // Simulate login logic
  if (username && password) {
    res.json({
      message: 'Login successful',
      token: 'mock-jwt-token',
    });
  } else {
    res.status(400).json({ error: 'Invalid credentials' });
  }
});

app.post('/api/auth/register', strictLimiter, (req, res) => {
  const { username, email, password } = req.body;

  // Simulate registration logic
  if (username && email && password) {
    res.status(201).json({
      message: 'User registered successfully',
      user: { username, email },
    });
  } else {
    res.status(400).json({ error: 'Missing required fields' });
  }
});

// Password reset with strict limiting
app.post('/api/auth/reset-password', strictLimiter, (req, res) => {
  const { email } = req.body;

  if (email) {
    res.json({ message: 'Password reset email sent' });
  } else {
    res.status(400).json({ error: 'Email required' });
  }
});

// Heavy operation endpoint (file upload simulation)
app.post('/api/upload', heavyOperationLimiter, (req, res) => {
  res.json({
    message: 'File upload successful',
    fileId: 'mock-file-id-' + Date.now(),
  });
});

// Custom rate limiter for specific endpoint
const customLimiter = createRateLimiter({
  windowMs: 30 * 1000, // 30 seconds
  max: 5, // 5 requests per 30 seconds
  message: 'Custom rate limit: Max 5 requests per 30 seconds',
});

app.get('/api/custom-limited', customLimiter, (req, res) => {
  res.json({ message: 'Custom rate-limited endpoint accessed' });
});

// Admin endpoints with very permissive limits
const adminLimiter = createRateLimiter({
  windowMs: 60 * 1000,
  max: 200,
  message: 'Admin rate limit exceeded',
});

app.get('/api/admin/stats', adminLimiter, (req, res) => {
  res.json({
    message: 'Admin stats',
    stats: { totalUsers: 100, activeUsers: 50 },
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error',
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Start server and connect to Redis
const startServer = async () => {
  try {
    // Connect to Redis first
    await connectRedis();
    console.log('Redis connection established');

    // Start Express server
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
      console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
      console.log('\nAvailable endpoints:');
      console.log(`  GET  http://localhost:${PORT}/health`);
      console.log(`  GET  http://localhost:${PORT}/api/public/data`);
      console.log(`  GET  http://localhost:${PORT}/api/search?q=test`);
      console.log(`  POST http://localhost:${PORT}/api/auth/login`);
      console.log(`  POST http://localhost:${PORT}/api/auth/register`);
      console.log(`  POST http://localhost:${PORT}/api/auth/reset-password`);
      console.log(`  POST http://localhost:${PORT}/api/upload`);
      console.log(`  GET  http://localhost:${PORT}/api/custom-limited`);
      console.log(`  GET  http://localhost:${PORT}/api/admin/stats`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  const { redisClient } = require('./config/redis');
  await redisClient.quit();
  process.exit(0);
});

startServer();
