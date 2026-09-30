# Spring Boot JWT Authentication Service

## Requirements
- Java 17+
- Maven

## Setup
```bash
mvn spring-boot:run
```
Server starts on `http://localhost:8080` with demo users:
- `alice` / `password`
- `admin` / `admin123`

## Authentication Flow
1. Login:
   ```bash
   curl -X POST http://localhost:8080/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"alice","password":"password"}'
   ```
   Response contains JWT access token.

2. Access protected resource:
   ```bash
   curl http://localhost:8080/api/greeting \
     -H "Authorization: Bearer <token>"
   ```

3. Logout (blacklists token):
   ```bash
   curl -X POST http://localhost:8080/api/auth/logout \
     -H "Authorization: Bearer <token>"
   ```

Subsequent requests with the same token are rejected. Tokens auto-expire after 15 minutes (`app.jwt.expirationMs`). Update `app.jwt.secret` with a secure Base64-encoded key for production.
