import 'dotenv/config';
import express from 'express';
import { validate, customJoi as Joi } from './validator.js';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

const createUserSchema = {
  body: Joi.object({
    name: Joi.string().min(3).required(),
    email: Joi.string().email().required(),
    age: Joi.even().min(18).required(),
    role: Joi.string().valid('user', 'admin').default('user')
  })
};

app.post('/users', validate(createUserSchema), (req, res) => {
  res.status(201).json({ user: req.body });
});

const paginationSchema = {
  query: Joi.object({
    page: Joi.number().integer().min(1).default(1),
    pageSize: Joi.number().integer().min(1).max(100).default(10)
  })
};

app.get('/items/:id', validate({ params: Joi.object({ id: Joi.string().uuid().required() }), ...paginationSchema }), (req, res) => {
  res.json({ params: req.params, query: req.query });
});

app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ message: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`Validation API running on http://localhost:${PORT}`);
});
