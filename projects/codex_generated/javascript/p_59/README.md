# Log Aggregator Service

Express service accepting JSON log payloads and recording them with Winston. Logs are written to console and rotated daily files (`logs/app-%DATE%.log` with 10MB size limit, 14-day retention).

## Setup
```bash
npm install
npm start
```

Optional env vars: `PORT` (default 5000).

## API
`POST /logs`
```json
{
  "level": "warn",
  "message": "User exceeded quota",
  "source": "billing-service",
  "meta": { "userId": 123 }
}
```
`level` defaults to `info`. `message` is required.

`GET /health` – service status.

Winston transports include console (colorized) and rotating file (`winston-daily-rotate-file`).
