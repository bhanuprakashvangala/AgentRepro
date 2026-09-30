import 'dotenv/config';
import express from 'express';
import geoip from 'geoip-lite';

const PORT = process.env.PORT || 3000;
const CACHE_TTL = Number(process.env.CACHE_TTL_SECONDS || 3600);
const app = express();

const cache = new Map();

function getFromCache(ip) {
  const entry = cache.get(ip);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL * 1000) {
    cache.delete(ip);
    return null;
  }
  return entry.data;
}

function setCache(ip, data) {
  cache.set(ip, { data, timestamp: Date.now() });
}

app.get('/geolocate', (req, res) => {
  const ip = req.query.ip || req.ip;
  if (!ip) {
    return res.status(400).json({ message: 'IP address is required' });
  }

  const cached = getFromCache(ip);
  if (cached) {
    return res.json({ ...cached, source: 'cache' });
  }

  const geo = geoip.lookup(ip);
  if (!geo) {
    return res.status(404).json({ message: 'Location not found for IP' });
  }

  const data = {
    ip,
    city: geo.city || null,
    country: geo.country || null,
    coordinates: { latitude: geo.ll[0], longitude: geo.ll[1] }
  };
  setCache(ip, data);
  res.json({ ...data, source: 'lookup' });
});

app.get('/', (req, res) => {
  res.json({ status: 'Geolocation service ready', endpoint: '/geolocate?ip=' });
});

app.listen(PORT, () => {
  console.log(`Geolocation service running on http://localhost:${PORT}`);
});
