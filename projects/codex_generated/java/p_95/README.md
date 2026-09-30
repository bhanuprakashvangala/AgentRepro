# HikariCP Pool Manager

Spring Boot app demonstrating HikariCP connection pool configuration, monitoring, and timeout handling using an in-memory H2 database.

## Features
- HikariCP configured with optimal defaults (pool size, idle timeout, max lifetime)
- `/api/pool/metrics` endpoint showing pool statistics and connection health check
- Spring Boot Actuator metrics enabled for integration with monitoring systems
- Connection timeout set to 30 seconds to handle stalled requests gracefully

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_95
mvn clean package
mvn spring-boot:run
```

## Sample API
```bash
curl http://localhost:8080/api/pool/metrics
```
Example response:
```json
{
  "totalConnections": 3,
  "activeConnections": 1,
  "idleConnections": 2,
  "threadsAwaiting": 0,
  "health": true
}
```

## Configuration
Edit `src/main/resources/application.properties` to adjust pool size, timeouts, or switch to another JDBC URL.

## Stop
Use `Ctrl+C` to stop the application.
