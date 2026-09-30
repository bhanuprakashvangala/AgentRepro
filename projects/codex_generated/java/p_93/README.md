# Bucket4j Rate Limiter

Spring Boot application demonstrating Bucket4j token-bucket rate limiting applied to REST endpoints.

## Features
- Bucket4j `Bandwidth` with configurable capacity/refill
- Request-scoped rate limiting via `OncePerRequestFilter`
- Client identification via `X-Client-Id` header (fallback to IP)
- Returns HTTP 429 when the bucket is empty

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_93
mvn clean package
mvn spring-boot:run
```

## Configuration
`src/main/resources/application.properties` exposes:
- `ratelimiter.capacity` – max tokens per bucket
- `ratelimiter.refill.tokens` – tokens added per period
- `ratelimiter.refill.period-seconds` – refill period in seconds

## Test Endpoint
```bash
curl -H "X-Client-Id: demo" http://localhost:8080/api/greet?name=Alice
```
After consuming the configured number of tokens within the period, the service returns:
```json
{"error":"Too many requests"}
```
with status `429 Too Many Requests`.

## Stop
Press `Ctrl+C` to stop Spring Boot.
