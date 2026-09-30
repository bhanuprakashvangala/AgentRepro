const express = require('express');
const { customAlphabet } = require('nanoid');
const Link = require('../models/Link');

const router = express.Router();
const nanoid = customAlphabet('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 7);

const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

router.post(
  '/',
  asyncHandler(async (req, res) => {
    const { originalUrl, expiresInDays } = req.body;
    if (!originalUrl) {
      return res.status(400).json({ message: '`originalUrl` is required' });
    }

    let shortCode = nanoid();
    while (await Link.exists({ shortCode })) {
      shortCode = nanoid();
    }

    const link = new Link({ originalUrl, shortCode });
    if (expiresInDays) {
      const days = Number(expiresInDays);
      if (!Number.isNaN(days) && days > 0) {
        link.expiresAt = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
      }
    }

    await link.save();
    return res.status(201).json({
      shortCode: link.shortCode,
      originalUrl: link.originalUrl,
      expiresAt: link.expiresAt,
      createdAt: link.createdAt
    });
  })
);

router.get(
  '/:code/stats',
  asyncHandler(async (req, res) => {
    const link = await Link.findOne({ shortCode: req.params.code }).lean();
    if (!link) {
      return res.status(404).json({ message: 'Short link not found' });
    }
    return res.json({
      shortCode: link.shortCode,
      originalUrl: link.originalUrl,
      createdAt: link.createdAt,
      expiresAt: link.expiresAt,
      clickCount: link.clickCount,
      analytics: link.analytics
    });
  })
);

module.exports = router;
