# Redis Session Server

Express session handling with Redis storage (`connect-redis`). Supports TTL, regeneration, and destruction endpoints.

## Setup
Ensure Redis is running (default `redis://127.0.0.1:6379`).

```bash
npm install
SESSION_SECRET=mysecret npm start
```
Optional env vars: `PORT`, `REDIS_URL`, `SESSION_TTL_SECONDS`.

## Endpoints
- `GET /` – increments `views` count in session.
- `GET /regen` – regenerates session ID (mitigates fixation).
- `GET /destroy` – destroys session.

Cookies use `rolling` to refresh TTL. Modify for HTTPS (`cookie.secure = true`) in production.
