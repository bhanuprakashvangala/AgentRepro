# RestTemplate Client Demo

Spring Boot sample demonstrating how to call external REST APIs with `RestTemplate`, handle responses/errors, and retry failed requests using exponential backoff.

The app proxies the public JSONPlaceholder posts API (`https://jsonplaceholder.typicode.com`) and exposes local endpoints for GET/POST/PUT/DELETE interactions.

## Features
- `RestTemplate` configured with connect/read timeouts
- CRUD operations implemented in `ExternalApiClient`
- Error handling with custom `ApiClientException` and global `@RestControllerAdvice`
- Retries (max 3 attempts) with exponential backoff using Spring Retry

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- Internet access (the sample targets the public JSONPlaceholder API)

## Run
```bash
cd 1-GPT/p_85
mvn clean package
mvn spring-boot:run
```

The service listens on `http://localhost:8080`.

## Sample Requests
- List posts:
  ```bash
  curl http://localhost:8080/api/posts
  ```
- Create a post:
  ```bash
  curl -X POST http://localhost:8080/api/posts \
    -H "Content-Type: application/json" \
    -d '{"title":"Hello","body":"From RestTemplate client","userId":1}'
  ```
- Update a post:
  ```bash
  curl -X PUT http://localhost:8080/api/posts/1 \
    -H "Content-Type: application/json" \
    -d '{"title":"Updated","body":"Updated body","userId":1}'
  ```
- Delete a post:
  ```bash
  curl -X DELETE http://localhost:8080/api/posts/1
  ```

On HTTP errors or connectivity issues, the client retries up to 3 times with exponential backoff (500ms, 1s, 2s). Failures after retries return a `502` response with details in JSON.

## Configuration
- `client.base-url` in `src/main/resources/application.properties` sets the remote API root
- Adjust retry behavior by editing annotations in `ExternalApiClient`
- Logging level is configured via `logging.level.com.example.restclient`
