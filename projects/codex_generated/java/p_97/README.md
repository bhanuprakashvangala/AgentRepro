# Spring Boot Health Check Service

This Spring Boot application exposes a health endpoint that aggregates database connectivity, an external service check, and selected metrics. It uses Spring Boot Actuator along with a custom health indicator.

## Features
- Actuator `/actuator/health` and `/actuator/metrics` endpoints exposed
- Custom `/api/health` endpoint returning consolidated health status & metrics
- Database connectivity check (H2 in-memory database by default)
- External service availability check using configurable URL and timeout
- Connection pool metrics (HikariCP)

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_97
mvn clean package
mvn spring-boot:run
```

## Endpoints
- `GET /api/health` – Composite health status and metrics
- `GET /actuator/health` – Standard Actuator health details
- `GET /actuator/metrics` – Actuator metrics listing

`/api/health` sample response:
```json
{
  "status": "UP",
  "components": {
    "db": { "status": "UP", "details": { "database": "H2", "validationQuery": "isValid()" } },
    "externalService": { "status": "UP", "details": { "url": "https://example.com", "status": 200 } }
  },
  "metrics": {
    "process.uptime": 12.345,
    "connectionPool": { "total": 3, "active": 0, "idle": 3, "threadsAwaiting": 0 }
  }
}
```

## Configuration
Control the external service health check in `src/main/resources/application.properties`:
```
health.external.url=https://example.com
health.external.timeout-seconds=2
```

Replace with an accessible endpoint in your environment if needed.

## Stop
Press `Ctrl+C` to stop the application.
