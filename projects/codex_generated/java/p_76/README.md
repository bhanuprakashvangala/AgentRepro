# Spring Boot CRUD API with JPA & MySQL

## Requirements
- Java 17+
- Maven
- MySQL instance (e.g. local Docker)

## Setup
1. Create database:
   ```sql
   CREATE DATABASE books_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Update `src/main/resources/application.properties` with your MySQL credentials.
3. Build & run:
   ```bash
   mvn spring-boot:run
   ```

Server listens on `http://localhost:8080` and exposes CRUD endpoints for `Book` entity at `/api/books`.

### Example Requests
- `POST /api/books` body `{ "title": "Sample", "author": "Author", "pages": 120 }`
- `GET /api/books`
- `GET /api/books/{id}`
- `PUT /api/books/{id}`
- `DELETE /api/books/{id}`

Validation errors return 400 with field messages. Missing resources return 404 via global handler.
