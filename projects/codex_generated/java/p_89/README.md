# Data Validation Service

Spring Boot REST API demonstrating Hibernate Validator with built-in and custom constraints. Incoming DTOs are validated, and detailed error responses are returned when rules fail.

## Features
- `spring-boot-starter-validation` (Hibernate Validator) integrated with REST controllers
- Custom constraint `@NoDisposableEmail` rejecting addresses from disposable domains
- Rich error responses listing field, rejected value, and reason
- Global exception handler covering both body and parameter validation

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_89
mvn clean package
mvn spring-boot:run
```

The service listens at `http://localhost:8080`.

## Example Request
```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "Taylor",
        "lastName": "Jordan",
        "email": "taylor@mailinator.com",
        "phoneNumber": "12345",
        "roles": ["GUEST"]
      }'
```

Response (`400 Bad Request`):
```json
{
  "timestamp": "2024-06-01T10:15:30.123Z",
  "message": "Validation failed",
  "errors": [
    { "field": "email", "rejectedValue": "taylor@mailinator.com", "reason": "Email domain 'mailinator.com' is not permitted" },
    { "field": "phoneNumber", "rejectedValue": "12345", "reason": "Phone number must be between 10 and 15 digits" },
    { "field": "roles[0]", "rejectedValue": "GUEST", "reason": "Role must be ADMIN, USER, or ANALYST" }
  ]
}
```

Valid request:
```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
        "firstName": "Morgan",
        "lastName": "Lee",
        "email": "morgan@example.org",
        "phoneNumber": "5551239876",
        "roles": ["ADMIN", "ANALYST"]
      }'
```

Response:
```json
{ "status": "created", "userId": "..." }
```

## Customization
- Extend `@NoDisposableEmail` by supplying `blacklist` attribute on field-level usage if needed.
- Add more DTOs and validators by following the same pattern.

## Stop
Use `Ctrl+C` in the terminal where Spring Boot is running.
