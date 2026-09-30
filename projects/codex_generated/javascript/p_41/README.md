# User Management REST API

Express-based REST API with MongoDB (Mongoose) integration for basic user management. Includes CRUD endpoints, input validation, and centralized error handling.

## Setup
```bash
npm install
npm run dev
```
By default the API connects to `mongodb://127.0.0.1:27017/user_management`. Override with:
```bash
MONGO_URI=mongodb://localhost:27017/mydb npm start
```

## Endpoints
- `GET /api/users` – List users
- `POST /api/users` – Create user `{ name, email, role?, active? }`
- `GET /api/users/:id`
- `PUT /api/users/:id`
- `DELETE /api/users/:id`

Validation is performed with `express-validator`. Errors return JSON with details. Responses use standard HTTP status codes: `201` on create, `204` on delete, `404` when not found, etc.

Logging is provided by `morgan`. The app exports the Express instance (`module.exports = app`) for testing or further integration.
