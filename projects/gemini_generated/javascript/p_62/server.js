require('dotenv').config();
const express = require('express');
const axios = require('axios');
const NodeCache = require('node-cache');

const app = express();
const cache = new NodeCache({ stdTTL: 3600 }); // Cache for 1 hour

const API_KEY = process.env.API_KEY;
const API_URL = `https://v6.exchangerate-api.com/v6/${API_KEY}/latest/USD`;

// Fetch exchange rates
const getRates = async () => {
    const cachedRates = cache.get('rates');
    if (cachedRates) {
        console.log('Using cached rates');
        return cachedRates;
    }

    try {
        console.log('Fetching new rates');
        const response = await axios.get(API_URL);
        const rates = response.data.conversion_rates;
        cache.set('rates', rates);
        return rates;
    } catch (error) {
        console.error('Error fetching exchange rates:', error.message);
        throw new Error('Could not fetch exchange rates');
    }
};

// Convert currency
app.get('/convert', async (req, res) => {
    const { from, to, amount } = req.query;

    if (!from || !to || !amount) {
        return res.status(400).json({ error: 'Missing required query parameters: from, to, amount' });
    }

    try {
        const rates = await getRates();
        const fromRate = rates[from.toUpperCase()];
        const toRate = rates[to.toUpperCase()];

        if (!fromRate || !toRate) {
            return res.status(400).json({ error: 'Invalid currency code' });
        }

        const convertedAmount = (amount / fromRate) * toRate;
        res.json({ result: convertedAmount });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
