import Joi from 'joi';

export function validate(schema) {
  return (req, res, next) => {
    const data = {};
    if (schema.body) {
      const { value, error } = schema.body.validate(req.body, { abortEarly: false });
      if (error) return respondError(error, res);
      req.body = value;
    }
    if (schema.params) {
      const { value, error } = schema.params.validate(req.params, { abortEarly: false });
      if (error) return respondError(error, res);
      req.params = value;
    }
    if (schema.query) {
      const { value, error } = schema.query.validate(req.query, { abortEarly: false });
      if (error) return respondError(error, res);
      req.query = value;
    }
    next();
  };
}

function respondError(error, res) {
  const details = error.details.map((detail) => ({
    message: detail.message,
    path: detail.path.join('.'),
    type: detail.type
  }));
  return res.status(400).json({ message: 'Validation failed', errors: details });
}

export const customJoi = Joi.extend((joi) => ({
  type: 'even',
  base: joi.number().integer(),
  messages: {
    'even.base': '{{#label}} must be an even integer'
  },
  validate(value, helpers) {
    if (value % 2 !== 0) {
      return { value, errors: helpers.error('even.base') };
    }
  }
}));
