const express = require('express');
const mongoose = require('mongoose');
const axios = require('axios');
const os = require('os');
const process = require('process');

const app = express();

// MongoDB Connection (for health check)
const MONGO_URI = 'mongodb://localhost:27017/health_check_db';

// External service to check (example: Google)
const EXTERNAL_SERVICE_URL = 'https://www.google.com';

app.get('/health', async (req, res) => {
    const health = {
        status: 'UP',
        checks: {},
        system: {
            uptime: process.uptime(),
            memoryUsage: process.memoryUsage(),
            platform: os.platform(),
            arch: os.arch(),
            cpus: os.cpus().length
        }
    };

    // Check database connectivity
    try {
        await mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true, serverSelectionTimeoutMS: 2000 });
        health.checks.database = { status: 'UP' };
    } catch (error) {
        health.status = 'DOWN';
        health.checks.database = { status: 'DOWN', error: error.message };
    }

    // Check external service availability
    try {
        await axios.get(EXTERNAL_SERVICE_URL, { timeout: 2000 });
        health.checks.externalService = { status: 'UP' };
    } catch (error) {
        health.status = 'DOWN';
        health.checks.externalService = { status: 'DOWN', error: error.message };
    }

    if (health.status === 'UP') {
        res.status(200).json(health);
    } else {
        res.status(503).json(health);
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
