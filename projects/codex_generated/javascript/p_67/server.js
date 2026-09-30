import 'dotenv/config';
import express from 'express';
import session from 'express-session';
import connectRedis from 'connect-redis';
import { createClient } from 'redis';

const PORT = process.env.PORT || 4000;
const SESSION_SECRET = process.env.SESSION_SECRET || 'super-secret';
const REDIS_URL = process.env.REDIS_URL || 'redis://127.0.0.1:6379';
const SESSION_TTL = Number(process.env.SESSION_TTL_SECONDS || 1800);

const RedisStore = connectRedis(session);
const redisClient = createClient({ url: REDIS_URL });
redisClient.on('error', (err) => console.error('Redis error', err));
await redisClient.connect();

const store = new RedisStore({ client: redisClient, prefix: 'sess:' });

const app = express();
app.use(express.json());

app.use(
  session({
    store,
    secret: SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
      maxAge: SESSION_TTL * 1000,
      httpOnly: true,
      secure: false
    },
    rolling: true
  })
);

app.get('/', (req, res) => {
  req.session.views = (req.session.views || 0) + 1;
  res.json({ message: 'Session active', sessionId: req.sessionID, views: req.session.views });
});

app.get('/regen', (req, res, next) => {
  req.session.regenerate((err) => {
    if (err) return next(err);
    req.session.regeneratedAt = new Date().toISOString();
    res.json({ message: 'Session regenerated', sessionId: req.sessionID });
  });
});

app.get('/destroy', (req, res, next) => {
  req.session.destroy((err) => {
    if (err) return next(err);
    res.clearCookie('connect.sid');
    res.json({ message: 'Session destroyed' });
  });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Server error' });
});

app.listen(PORT, () => {
  console.log(`Session server on http://localhost:${PORT}`);
});
