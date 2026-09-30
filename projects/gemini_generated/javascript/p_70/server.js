const express = require('express');
const geoip = require('geoip-lite');
const NodeCache = require('node-cache');

const app = express();
const cache = new NodeCache({ stdTTL: 3600 }); // Cache for 1 hour

app.get('/geocode', (req, res) => {
    const ip = req.query.ip || req.ip; // Use query IP or request IP

    if (!ip) {
        return res.status(400).json({ error: 'IP address is required.' });
    }

    const cachedResult = cache.get(ip);
    if (cachedResult) {
        console.log('Using cached result for IP:', ip);
        return res.json(cachedResult);
    }

    const geo = geoip.lookup(ip);

    if (geo) {
        const result = {
            ip: ip,
            country: geo.country,
            city: geo.city,
            latitude: geo.ll[0],
            longitude: geo.ll[1]
        };
        cache.set(ip, result);
        res.json(result);
    } else {
        res.status(404).json({ error: 'Geolocation data not found for this IP.' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
