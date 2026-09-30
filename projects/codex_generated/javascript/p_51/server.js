require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const Link = require('./models/Link');
const linkRoutes = require('./routes/linkRoutes');

const app = express();
const PORT = process.env.PORT || 4000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/url_shortener';

app.use(bodyParser.json());
app.use('/api/links', linkRoutes);

app.get('/:code', async (req, res, next) => {
  try {
    const link = await Link.findOne({ shortCode: req.params.code });
    if (!link || link.hasExpired()) {
      return res.status(404).send('Link expired or not found');
    }
    link.clickCount += 1;
    link.analytics.push({
      referrer: req.get('referer') || 'direct',
      ipAddress: req.ip,
      userAgent: req.get('user-agent')
    });
    await link.save();
    return res.redirect(link.originalUrl);
  } catch (error) {
    return next(error);
  }
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal server error' });
});

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log('Connected to MongoDB');
    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  })
  .catch((err) => {
    console.error('Failed to connect to MongoDB', err);
    process.exit(1);
  });
