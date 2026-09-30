# Rate Limiter using Bucket4j

This project demonstrates how to implement a rate limiter using Spring Boot and Bucket4j library.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd rate-limiter
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

There are two endpoints:

- `/api/rate-limited`: This endpoint is rate-limited to 5 requests per 10 seconds.
- `/api/unlimited`: This endpoint is not rate-limited.

### Testing the Rate-Limited Endpoint

You can test the rate-limited endpoint using `curl` or a web browser. Try to make more than 5 requests within 10 seconds to `http://localhost:8080/api/rate-limited`.

**Example using cURL:**

```bash
for i in $(seq 1 10); do curl -v http://localhost:8080/api/rate-limited; sleep 1; done
```

You should see `200 OK` responses for the first 5 requests and then `429 Too Many Requests` responses for subsequent requests within the 10-second window.

### Testing the Unlimited Endpoint

```bash
curl http://localhost:8080/api/unlimited
```

This endpoint will always return `200 OK`.
