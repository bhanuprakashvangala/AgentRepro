import 'dotenv/config';
import express from 'express';
import bodyParser from 'body-parser';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const PORT = process.env.PORT || 3000;
const ACCESS_SECRET = process.env.ACCESS_SECRET || 'access-secret';
const REFRESH_SECRET = process.env.REFRESH_SECRET || 'refresh-secret';
const ACCESS_TTL = process.env.ACCESS_TTL || '15m';
const REFRESH_TTL = process.env.REFRESH_TTL || '7d';

const refreshStore = new Map();

const app = express();
app.use(bodyParser.json());

function generateToken(payload, secret, expiresIn) {
  return jwt.sign(payload, secret, { expiresIn });
}

app.post('/token', (req, res) => {
  const { userId } = req.body || {};
  if (!userId) {
    return res.status(400).json({ message: '`userId` required' });
  }
  const accessToken = generateToken({ sub: userId }, ACCESS_SECRET, ACCESS_TTL);
  const refreshId = crypto.randomUUID();
  const refreshToken = generateToken({ sub: userId, jti: refreshId }, REFRESH_SECRET, REFRESH_TTL);
  refreshStore.set(refreshId, { userId, issuedAt: Date.now() });
  res.json({ accessToken, refreshToken });
});

app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body || {};
  if (!refreshToken) {
    return res.status(400).json({ message: '`refreshToken` required' });
  }
  try {
    const decoded = jwt.verify(refreshToken, REFRESH_SECRET);
    const record = refreshStore.get(decoded.jti);
    if (!record || record.userId !== decoded.sub) {
      return res.status(401).json({ message: 'Refresh token invalid or rotated' });
    }
    refreshStore.delete(decoded.jti);

    const newRefreshId = crypto.randomUUID();
    const newRefreshToken = generateToken({ sub: decoded.sub, jti: newRefreshId }, REFRESH_SECRET, REFRESH_TTL);
    refreshStore.set(newRefreshId, { userId: decoded.sub, issuedAt: Date.now() });

    const newAccessToken = generateToken({ sub: decoded.sub }, ACCESS_SECRET, ACCESS_TTL);
    res.json({ accessToken: newAccessToken, refreshToken: newRefreshToken });
  } catch (error) {
    res.status(401).json({ message: 'Invalid refresh token' });
  }
});

app.get('/verify', (req, res) => {
  const auth = req.get('Authorization') || '';
  const token = auth.replace('Bearer ', '');
  if (!token) {
    return res.status(400).json({ message: 'Bearer token required' });
  }
  try {
    const decoded = jwt.verify(token, ACCESS_SECRET);
    res.json({ valid: true, payload: decoded });
  } catch (error) {
    res.status(401).json({ message: 'Invalid token', error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`JWT service running on http://localhost:${PORT}`);
});
