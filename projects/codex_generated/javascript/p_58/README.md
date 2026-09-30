# JSON API Mock Server

Express-based JSON API that supports CRUD operations, filtering, and configurable response delays.

## Setup
```bash
npm install
npm start
```

Server listens on `http://localhost:4000`. Set `PORT` or `RESPONSE_DELAY` via env if needed.

## Endpoints
- `GET /api/posts` – list resources (supports `?author=Alice&published=true&limit=5&offset=0`).
- `GET /api/posts/:id`
- `POST /api/posts`
- `PUT /api/posts/:id`
- `DELETE /api/posts/:id`

Collections are dynamic; posting to `/api/tasks` auto-creates that collection. Append `?delay=500` to any request for per-request delay (ms).

Initial data seeded with sample `posts` collection. Responses are in-memory; restart resets state. Ideal for frontend prototyping.
