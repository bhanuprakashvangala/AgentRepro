# Joi Validation Middleware

Express middleware using Joi schemas for body/params/query validation, with custom rules.

## Setup
```bash
npm install
npm start
```

## Endpoints
- `POST /users`
  ```json
  { "name": "Alice", "email": "alice@example.com", "age": 24 }
  ```
  `age` uses custom Joi extension to require even integers.

- `GET /items/:id?page=2&pageSize=20`
  `id` must be UUID; query params validated and defaulted.

Validation errors return HTTP 400 with detailed messages and paths.
