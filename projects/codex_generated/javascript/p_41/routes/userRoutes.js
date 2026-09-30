const express = require('express');
const { body, param, validationResult } = require('express-validator');
const mongoose = require('mongoose');
const User = require('../models/User');

const router = express.Router();

const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

const handleValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  return next();
};

router.get(
  '/',
  asyncHandler(async (req, res) => {
    const users = await User.find().lean();
    res.json(users);
  })
);

router.post(
  '/',
  [
    body('name').isString().trim().isLength({ min: 2, max: 100 }),
    body('email').isEmail().normalizeEmail(),
    body('role').optional().isIn(['user', 'admin']),
    body('active').optional().isBoolean()
  ],
  handleValidation,
  asyncHandler(async (req, res) => {
    const { name, email, role, active } = req.body;
    const existing = await User.findOne({ email });
    if (existing) {
      return res.status(409).json({ message: 'User with this email already exists' });
    }
    const user = await User.create({ name, email, role, active });
    res.status(201).json(user);
  })
);

router.get(
  '/:id',
  [param('id').custom((value) => mongoose.Types.ObjectId.isValid(value))],
  handleValidation,
  asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id).lean();
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  })
);

router.put(
  '/:id',
  [
    param('id').custom((value) => mongoose.Types.ObjectId.isValid(value)),
    body('name').optional().isString().trim().isLength({ min: 2, max: 100 }),
    body('email').optional().isEmail().normalizeEmail(),
    body('role').optional().isIn(['user', 'admin']),
    body('active').optional().isBoolean()
  ],
  handleValidation,
  asyncHandler(async (req, res) => {
    const updates = req.body;
    if (updates.email) {
      const existing = await User.findOne({ email: updates.email, _id: { $ne: req.params.id } });
      if (existing) {
        return res.status(409).json({ message: 'Email already in use by another user' });
      }
    }
    const user = await User.findByIdAndUpdate(req.params.id, updates, { new: true, runValidators: true });
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user);
  })
);

router.delete(
  '/:id',
  [param('id').custom((value) => mongoose.Types.ObjectId.isValid(value))],
  handleValidation,
  asyncHandler(async (req, res) => {
    const user = await User.findByIdAndDelete(req.params.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.status(204).send();
  })
);

module.exports = router;
