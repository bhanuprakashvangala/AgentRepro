import express from 'express';
import { getCache, setCache } from './cache.js';

const app = express();
const PORT = process.env.PORT || 4000;

app.use(express.json());

app.post('/cache', async (req, res) => {
  const { key, value, ttl } = req.body || {};
  if (!key || value === undefined) {
    return res.status(400).json({ message: '`key` and `value` required' });
  }
  try {
    await setCache(key, value, ttl || 300);
    res.json({ message: 'Stored', key, ttl: ttl || 300 });
  } catch (error) {
    res.status(500).json({ message: 'Failed to set cache', error: error.message });
  }
});

app.get('/cache/:key', async (req, res) => {
  try {
    const value = await getCache(req.params.key);
    if (value === null) {
      return res.status(404).json({ message: 'Key not found' });
    }
    res.json({ key: req.params.key, value });
  } catch (error) {
    res.status(500).json({ message: 'Failed to get cache', error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Cache service listening on http://localhost:${PORT}`);
});
