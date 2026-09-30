import express from 'express';
import axios from 'axios';
import NodeCache from 'node-cache';

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize cache with 1 hour TTL (3600 seconds)
const cache = new NodeCache({ stdTTL: 3600, checkperiod: 600 });

// Free API endpoint for exchange rates (no API key required)
const EXCHANGE_RATE_API = 'https://api.exchangerate-api.com/v4/latest';

// Alternative: https://open.er-api.com/v6/latest (also free, no key required)

/**
 * Fetch exchange rates from external API
 * @param {string} baseCurrency - Base currency code (e.g., 'USD')
 * @returns {Promise<Object>} Exchange rates object
 */
async function fetchExchangeRates(baseCurrency = 'USD') {
  const cacheKey = `rates_${baseCurrency}`;

  // Check cache first
  const cachedRates = cache.get(cacheKey);
  if (cachedRates) {
    console.log(`Cache hit for ${baseCurrency}`);
    return cachedRates;
  }

  try {
    console.log(`Fetching fresh rates for ${baseCurrency} from API...`);
    const response = await axios.get(`${EXCHANGE_RATE_API}/${baseCurrency}`, {
      timeout: 5000,
      headers: {
        'Accept': 'application/json'
      }
    });

    const ratesData = {
      base: response.data.base,
      date: response.data.date,
      rates: response.data.rates,
      timestamp: Date.now()
    };

    // Store in cache
    cache.set(cacheKey, ratesData);
    console.log(`Cached rates for ${baseCurrency}`);

    return ratesData;
  } catch (error) {
    console.error('Error fetching exchange rates:', error.message);
    throw new Error('Failed to fetch exchange rates');
  }
}

/**
 * Convert amount from one currency to another
 * @param {number} amount - Amount to convert
 * @param {string} from - Source currency code
 * @param {string} to - Target currency code
 * @returns {Promise<Object>} Conversion result
 */
async function convertCurrency(amount, from, to) {
  const fromUpper = from.toUpperCase();
  const toUpper = to.toUpperCase();

  // Fetch rates based on source currency
  const ratesData = await fetchExchangeRates(fromUpper);

  // Check if target currency exists
  if (!ratesData.rates[toUpper]) {
    throw new Error(`Currency ${toUpper} not supported`);
  }

  // If converting from base currency
  if (fromUpper === ratesData.base) {
    const convertedAmount = amount * ratesData.rates[toUpper];
    return {
      from: fromUpper,
      to: toUpper,
      amount: amount,
      converted: parseFloat(convertedAmount.toFixed(4)),
      rate: ratesData.rates[toUpper],
      date: ratesData.date,
      cached: cache.has(`rates_${fromUpper}`)
    };
  }

  // If converting to a different currency, need to calculate cross rate
  const rateFrom = ratesData.rates[fromUpper] || 1;
  const rateTo = ratesData.rates[toUpper];
  const crossRate = rateTo / rateFrom;
  const convertedAmount = amount * crossRate;

  return {
    from: fromUpper,
    to: toUpper,
    amount: amount,
    converted: parseFloat(convertedAmount.toFixed(4)),
    rate: parseFloat(crossRate.toFixed(6)),
    date: ratesData.date,
    cached: cache.has(`rates_${fromUpper}`)
  };
}

// Middleware
app.use(express.json());

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'Currency Converter API',
    version: '1.0.0',
    endpoints: {
      rates: 'GET /rates/:currency',
      convert: 'GET /convert?amount=100&from=USD&to=EUR',
      supported: 'GET /currencies',
      cache: 'GET /cache/stats'
    }
  });
});

// Get all exchange rates for a base currency
app.get('/rates/:currency?', async (req, res) => {
  try {
    const baseCurrency = (req.params.currency || 'USD').toUpperCase();
    const rates = await fetchExchangeRates(baseCurrency);

    res.json({
      success: true,
      data: rates,
      cached: cache.has(`rates_${baseCurrency}`)
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Convert currency
app.get('/convert', async (req, res) => {
  try {
    const { amount, from, to } = req.query;

    // Validation
    if (!amount || !from || !to) {
      return res.status(400).json({
        success: false,
        error: 'Missing required parameters: amount, from, to'
      });
    }

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      return res.status(400).json({
        success: false,
        error: 'Amount must be a positive number'
      });
    }

    const result = await convertCurrency(numAmount, from, to);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get list of supported currencies
app.get('/currencies', async (req, res) => {
  try {
    const rates = await fetchExchangeRates('USD');
    const currencies = Object.keys(rates.rates).sort();

    res.json({
      success: true,
      count: currencies.length,
      currencies: currencies
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get cache statistics
app.get('/cache/stats', (req, res) => {
  const stats = cache.getStats();
  const keys = cache.keys();

  res.json({
    success: true,
    stats: {
      keys: keys.length,
      hits: stats.hits,
      misses: stats.misses,
      hitRate: stats.hits > 0 ? ((stats.hits / (stats.hits + stats.misses)) * 100).toFixed(2) + '%' : '0%',
      cachedCurrencies: keys.map(k => k.replace('rates_', ''))
    }
  });
});

// Clear cache endpoint (optional)
app.delete('/cache', (req, res) => {
  cache.flushAll();
  res.json({
    success: true,
    message: 'Cache cleared successfully'
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Currency Converter API running on port ${PORT}`);
  console.log(`Try: http://localhost:${PORT}`);
  console.log(`Cache TTL: 1 hour`);
});
