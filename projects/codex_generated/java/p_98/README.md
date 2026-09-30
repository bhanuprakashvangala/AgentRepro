# Redisson Distributed Lock Manager

Spring Boot service illustrating distributed locks using Redisson on Redis. Supports regular and fair locks, configurable wait/lease times, and safe release handling.

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- Redis server (default `redis://127.0.0.1:6379`)

## Build & Run
```bash
cd 1-GPT/p_98
mvn clean package
mvn spring-boot:run
```

## API
`POST /api/lock/execute`

Body:
```json
{
  "name": "resource-key",
  "fair": true,
  "waitSeconds": 5,
  "leaseSeconds": 30,
  "executionMillis": 1500
}
```

- `name` – lock identifier shared across instances
- `fair` – enable Redisson fair lock
- `waitSeconds` – max time to wait for lock (defaults to 5s)
- `leaseSeconds` – auto-release time (defaults to 30s)
- `executionMillis` – simulated work duration while holding lock

Responses:
- `200 OK` with `{ "status": "executed" }` when lock obtained
- `409 CONFLICT` with `{ "status": "lock_failed" }` when acquisition fails/timeout

Configuration values (Redis address/password) are editable in `src/main/resources/application.properties`.

## Stop
Use `Ctrl+C` to stop the Spring Boot application.
