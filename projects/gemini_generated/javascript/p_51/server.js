const express = require('express');
const mongoose = require('mongoose');
const shortid = require('shortid');

const app = express();
app.use(express.json());

// MongoDB Connection
const MONGO_URI = 'mongodb://localhost:27017/url_shortener';
mongoose.connect(MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Failed to connect to MongoDB', err));

// URL Schema
const urlSchema = new mongoose.Schema({
    originalUrl: String,
    shortUrl: {
        type: String,
        required: true,
        default: shortid.generate
    },
    clicks: {
        type: Number,
        required: true,
        default: 0
    },
    referrers: [String],
    expiresAt: {
        type: Date,
        default: null
    }
});

const Url = mongoose.model('Url', urlSchema);

// Shorten a URL
app.post('/shorten', async (req, res) => {
    const { originalUrl, expiresAt } = req.body;

    if (!originalUrl) {
        return res.status(400).json({ error: 'Original URL is required.' });
    }

    try {
        let url = await Url.findOne({ originalUrl });

        if (url) {
            return res.json(url);
        }

        const newUrl = new Url({
            originalUrl,
            expiresAt
        });

        await newUrl.save();
        res.json(newUrl);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

// Redirect to the original URL
app.get('/:shortUrl', async (req, res) => {
    try {
        const url = await Url.findOne({ shortUrl: req.params.shortUrl });

        if (!url) {
            return res.status(404).json({ error: 'URL not found' });
        }

        if (url.expiresAt && url.expiresAt < new Date()) {
            return res.status(410).json({ error: 'URL has expired' });
        }

        url.clicks++;
        const referrer = req.get('Referrer');
        if (referrer) {
            url.referrers.push(referrer);
        }
        await url.save();

        res.redirect(url.originalUrl);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

// Get analytics for a URL
app.get('/analytics/:shortUrl', async (req, res) => {
    try {
        const url = await Url.findOne({ shortUrl: req.params.shortUrl });

        if (!url) {
            return res.status(404).json({ error: 'URL not found' });
        }

        res.json({
            originalUrl: url.originalUrl,
            shortUrl: url.shortUrl,
            clicks: url.clicks,
            referrers: url.referrers
        });
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Server error' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
