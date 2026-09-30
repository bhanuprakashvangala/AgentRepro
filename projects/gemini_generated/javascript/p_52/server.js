const express = require('express');
const { rateLimit } = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const { createClient } = require('redis');

const app = express();

// Create a Redis client
const client = createClient({
    // Replace with your Redis server details
    url: 'redis://localhost:6379'
});

client.on('error', (err) => console.log('Redis Client Error', err));

(async () => {
    await client.connect();
})();

// General rate limiter
const generalLimiter = rateLimit({
    store: new RedisStore({
        sendCommand: (...args) => client.sendCommand(args),
    }),
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again after 15 minutes'
});

// Specific rate limiter for a sensitive endpoint
const sensitiveEndpointLimiter = rateLimit({
    store: new RedisStore({
        sendCommand: (...args) => client.sendCommand(args),
    }),
    windowMs: 5 * 60 * 1000, // 5 minutes
    max: 10, // limit each IP to 10 requests per windowMs
    message: 'Too many requests to this endpoint, please try again after 5 minutes'
});

// Apply the general rate limiter to all requests
app.use(generalLimiter);

// Public endpoint
app.get('/', (req, res) => {
    res.send('This is a public endpoint.');
});

// Sensitive endpoint with a specific rate limiter
app.get('/sensitive', sensitiveEndpointLimiter, (req, res) => {
    res.send('This is a sensitive endpoint.');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
