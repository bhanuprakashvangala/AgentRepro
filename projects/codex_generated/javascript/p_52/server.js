require('dotenv').config();
const express = require('express');
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const { Redis } = require('ioredis');

const PORT = process.env.PORT || 4000;
const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';

const redisClient = new Redis(REDIS_URL);
redisClient.on('connect', () => console.log('Connected to Redis'));
redisClient.on('error', (err) => console.error('Redis error', err));

const createLimiter = ({ windowMs, max, prefix, message }) =>
  rateLimit({
    windowMs,
    max,
    standardHeaders: 'draft-7',
    legacyHeaders: false,
    handler: (req, res) => {
      res.status(429).json({
        message: message || 'Too many requests',
        retryAfterSeconds: Math.ceil(windowMs / 1000)
      });
    },
    store: new RedisStore({
      prefix: `rl:${prefix}:`,
      sendCommand: (...args) => redisClient.call(...args)
    })
  });

const app = express();
app.use(express.json());

const publicLimiter = createLimiter({
  windowMs: 15 * 60 * 1000,
  max: 100,
  prefix: 'public',
  message: 'Too many requests to /api/public. Try again later.'
});

const authLimiter = createLimiter({
  windowMs: 60 * 1000,
  max: 5,
  prefix: 'login',
  message: 'Too many login attempts. Please wait a minute.'
});

const searchLimiter = createLimiter({
  windowMs: 60 * 1000,
  max: 30,
  prefix: 'search'
});

app.get('/', (req, res) => {
  res.json({ status: 'Rate limiter demo running' });
});

app.get('/api/public', publicLimiter, (req, res) => {
  res.json({ data: 'Public content response' });
});

app.post('/api/login', authLimiter, (req, res) => {
  res.json({ message: 'Login successful (placeholder)' });
});

app.get('/api/search', searchLimiter, (req, res) => {
  res.json({ results: [], query: req.query.q || '' });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});

process.on('SIGINT', async () => {
  await redisClient.quit();
  process.exit(0);
});
