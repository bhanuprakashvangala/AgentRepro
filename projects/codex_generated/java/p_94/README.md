# JSON Parser & Validator

Spring Boot service that parses JSON strings using Jackson and validates them against JSON Schema (Everit implementation).

## Features
- Parse raw JSON request body into native Java objects
- Validate using JSON Schema (draft 2020-12)
- Graceful error handling for malformed JSON or missing schemas
- Sample `user` schema included

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_94
mvn clean package
mvn spring-boot:run
```

## API Usage
`POST /api/json/validate`

Request body:
```json
{
  "schemaName": "user",
  "json": "{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"age\":25}"
}
```

Response:
```json
{
  "valid": true,
  "errors": [],
  "parsedObject": {
    "name": "Alice",
    "email": "alice@example.com",
    "age": 25
  }
}
```

Invalid example:
```json
{
  "schemaName": "user",
  "json": "{\"name\":\"Bob\"}"
}
```
Response:
```json
{
  "valid": false,
  "errors": [
    "required key [email] not found"
  ],
  "parsedObject": {
    "name": "Bob"
  }
}
```

If the JSON payload is malformed, status `400` is returned with message `Invalid JSON: ...`.

To add new schemas, place them in `src/main/resources/schemas/` and reference by filename (without extension).

## Stop
Use `Ctrl+C` to terminate the Spring Boot application.
