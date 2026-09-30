# Rate Limiter Middleware Demo

Express server showcasing per-endpoint rate limiting with Redis-backed storage using `express-rate-limit` + `rate-limit-redis`.

## Setup
```bash
npm install
```
Ensure Redis is running (`redis://127.0.0.1:6379` default). Override with `REDIS_URL` env.

## Run
```bash
npm start
```
Server listens on `http://localhost:4000` (override with `PORT`).

## Endpoints & Limits
- `GET /api/public` – 100 requests / 15 minutes per IP.
- `POST /api/login` – 5 requests / minute per IP (protects brute-force).
- `GET /api/search` – 30 requests / minute per IP.

Exceeding limits returns `429` with JSON body:
```json
{
  "message": "Too many login attempts. Please wait a minute.",
  "retryAfterSeconds": 60
}
```

## Notes
- Shared Redis store enables distributed rate limiting across multiple instances.
- `standardHeaders: 'draft-7'` enables `RateLimit-*` headers.
- Customize prefixes / windows / max via `createLimiter` helper.
