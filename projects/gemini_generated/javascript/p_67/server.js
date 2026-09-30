const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const app = express();

// Create a Redis client
const redisClient = createClient({
    url: 'redis://localhost:6379'
});

redisClient.on('error', (err) => console.log('Redis Client Error', err));

(async () => {
    await redisClient.connect();
})();

// Session middleware
app.use(session({
    store: new RedisStore({ client: redisClient }),
    secret: 'my-super-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false, // set to true if you're using https
        httpOnly: true,
        maxAge: 1000 * 60 * 10 // 10 minutes
    }
}));

// Routes
app.get('/', (req, res) => {
    if (req.session.views) {
        req.session.views++;
        res.send(`<p>Views: ${req.session.views}</p><p>Expires in: ${req.session.cookie.maxAge / 1000}s</p>`);
    } else {
        req.session.views = 1;
        res.send('Welcome to the session demo. Refresh!');
    }
});

// Regenerate session
app.get('/regenerate', (req, res) => {
    req.session.regenerate((err) => {
        if (err) {
            return res.status(500).send('Error regenerating session');
        }
        res.send('Session regenerated');
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
