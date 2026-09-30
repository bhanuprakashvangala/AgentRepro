import 'dotenv/config';
import express from 'express';
import axios from 'axios';

const PORT = process.env.PORT || 4000;
const BASE_CURRENCY = process.env.BASE_CURRENCY || 'USD';
const API_URL = process.env.RATES_API || `https://api.exchangerate.host/latest`;
const CACHE_TTL = Number(process.env.CACHE_TTL_SECONDS || 300);

let cache = { timestamp: 0, rates: null };

const app = express();

async function fetchRates(base) {
  const now = Date.now();
  if (cache.rates && now - cache.timestamp < CACHE_TTL * 1000 && cache.base === base) {
    return cache.rates;
  }
  const response = await axios.get(API_URL, { params: { base } });
  if (!response.data || !response.data.rates) {
    throw new Error('Invalid response from rates API');
  }
  cache = { timestamp: now, rates: response.data.rates, base };
  return cache.rates;
}

app.get('/convert', async (req, res) => {
  const { from = BASE_CURRENCY, to, amount = 1 } = req.query;
  if (!to) {
    return res.status(400).json({ message: '`to` currency is required' });
  }
  try {
    const numericAmount = Number(amount);
    if (Number.isNaN(numericAmount)) {
      return res.status(400).json({ message: '`amount` must be numeric' });
    }
    const rates = await fetchRates(from);
    const rate = rates[to];
    if (!rate) {
      return res.status(400).json({ message: `Rate for ${to} not available` });
    }
    const converted = numericAmount * rate;
    res.json({
      base: from,
      target: to,
      amount: numericAmount,
      converted,
      rate
    });
  } catch (error) {
    console.error('Conversion failed:', error.message);
    res.status(502).json({ message: 'Failed to fetch exchange rates' });
  }
});

app.get('/rates', async (req, res) => {
  try {
    const { base = BASE_CURRENCY } = req.query;
    const rates = await fetchRates(base);
    res.json({ base, rates, cachedAt: cache.timestamp });
  } catch (error) {
    res.status(502).json({ message: 'Failed to fetch exchange rates' });
  }
});

app.get('/', (req, res) => {
  res.json({ status: 'Currency converter API', endpoints: ['/convert', '/rates'] });
});

app.listen(PORT, () => {
  console.log(`Currency API running at http://localhost:${PORT}`);
});
