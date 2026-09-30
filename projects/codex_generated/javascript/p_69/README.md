# Health Check Service

Express server exposing `/health` endpoint verifying database connectivity, external service availability, and system metrics.

## Setup
```bash
npm install
npm start
```

Environment variables:
```
PORT=8080
MONGO_URI=mongodb://127.0.0.1:27017/health_db
EXTERNAL_SERVICE_URL=https://httpbin.org/get
```

## Endpoint
`GET /health` returns JSON:
```json
{
  "status": "up",
  "uptime": 123.45,
  "memory": { "rss": 123456 },
  "database": { "status": "up" },
  "externalService": { "status": "up" },
  "responseTimeMs": 12
}
```
If any dependency is down, the endpoint responds with HTTP 503 and details.
