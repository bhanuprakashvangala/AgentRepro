# API Versioning Service

Spring Boot REST API demonstrating URL-based (/v1/, /v2/) and header-based (`X-API-Version`) versioning with deprecation warnings and Swagger documentation.

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_99
mvn clean package
mvn spring-boot:run
```

## Endpoints
- `GET /api/v1/users` – URL versioned v1 (deprecated, adds `X-API-Deprecated` header)
- `GET /api/v2/users` – URL versioned v2
- `GET /api/users` + header `X-API-Version: 1` or `2` – header-based versioning
- Swagger UI: `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON: `http://localhost:8080/api-docs`

## Deprecation Warnings
When calling deprecated versions (v1 or header version 1), the response includes header `X-API-Deprecated: API version v1 is deprecated and will be removed soon.`

## Stop
Use `Ctrl+C` to stop the application.
