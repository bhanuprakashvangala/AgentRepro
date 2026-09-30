# Redis Cache Example

This is a simple Spring Boot application that demonstrates how to use Redis for caching.

## Prerequisites

- Docker installed and running
- Run `docker run -d -p 6379:6379 redis` to start a Redis container.

## Usage

1. Build the project:
   ```
   mvn clean install
   ```
2. Run the application:
   ```
   java -jar target/redis-cache-example-1.0-SNAPSHOT.jar
   ```

### API

- `POST /cache/{key}?ttl=<time-in-seconds>`: Set a value in the cache with a TTL.
- `GET /cache/{key}`: Get a value from the cache.
- `DELETE /cache/{key}`: Delete a value from the cache.