# Spring Redis Cache Manager

Spring Boot service demonstrating cache management backed by Redis using Spring Data Redis with the Jedis driver. Provides REST endpoints for get/set/delete operations, supports per-entry TTL, and enforces an application-level LRU eviction policy on top of Redis keys.

## Features
- Connects to Redis via Jedis (pooled connection factory)
- Cache operations exposed through `RedisCacheService` and `/api/cache` endpoints
- TTL support per entry (default 300 seconds) with automatic refresh on access
- Application-level eviction policy: maintains access order in a Redis sorted set and removes least recently used keys when `app.cache.max-entries` is exceeded

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- Redis server running locally on port 6379 (or configure host/port/password in `application.properties`)

## Run
```bash
cd 1-GPT/p_83
mvn clean package
mvn spring-boot:run
```

## Usage Examples
Set a cache value with a 60-second TTL:
```bash
curl -X POST http://localhost:8080/api/cache \
  -H "Content-Type: application/json" \
  -d '{"key":"user:1","value":"{\"name\":\"Alice\"}","ttlSeconds":60}'
```

Retrieve the cached value:
```bash
curl http://localhost:8080/api/cache/user:1
```

Delete a key:
```bash
curl -X DELETE http://localhost:8080/api/cache/user:1
```

## Configuration
- `app.cache.default-ttl-seconds` – default TTL applied when requests omit `ttlSeconds`
- `app.cache.max-entries` – maximum entries retained; least recently used keys are evicted when the limit is exceeded
- `app.cache.eviction-set-key` – Redis key used internally to track access order
- `app.redis.*` – Redis connection parameters

Redis server-level eviction policies (e.g., `ALLKEYS-LRU`) can still be configured independently. This sample demonstrates an application-managed LRU layer compatible with any Redis deployment.
