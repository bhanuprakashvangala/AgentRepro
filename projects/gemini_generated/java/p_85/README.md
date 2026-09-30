# REST API Client with RestTemplate

This project demonstrates a REST API client using Spring Boot's `RestTemplate` with retry logic and error handling.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd rest-api-client
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

This application interacts with the JSONPlaceholder API (`https://jsonplaceholder.typicode.com`).

### Get All Posts

```bash
curl http://localhost:8080/api/posts
```

### Get Post by ID

```bash
curl http://localhost:8080/api/posts/1
```

### Create a Post

```bash
curl -X POST -H "Content-Type: application/json" -d '
{
  "userId": 1,
  "title": "My New Post",
  "body": "This is the body of my new post."
}' http://localhost:8080/api/posts
```

### Update a Post

```bash
curl -X PUT -H "Content-Type: application/json" -d '
{
  "id": 1,
  "userId": 1,
  "title": "Updated Post Title",
  "body": "This is the updated body of my post."
}' http://localhost:8080/api/posts/1
```

### Delete a Post

```bash
curl -X DELETE http://localhost:8080/api/posts/1
```

## Retry Logic

The `ApiService` includes retry logic with exponential backoff for `ResourceAccessException` (e.g., network issues) and `HttpServerErrorException` (e.g., 5xx errors). If the external API is temporarily unavailable, the client will automatically retry the request a few times before failing.
