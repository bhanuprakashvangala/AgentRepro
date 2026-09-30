# Spring URL Shortener

RESTful URL shortening service built with Spring Boot and MongoDB. Generates unique short codes, tracks click analytics, and supports URL expiration.

## Features
- Spring Data MongoDB persistence with indexed short codes
- Unique alphanumeric short code generation
- Click tracking (count, timestamps, user agent, IP)
- Optional TTL/expiration per URL
- JSON API for creating, fetching info, and redirecting

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- MongoDB running locally (`mongodb://localhost:27017` by default)

## Configure
Adjust Mongo URI in `src/main/resources/application.properties` if needed:
```
spring.data.mongodb.uri=mongodb://localhost:27017/urlshortener
```

## Build & Run
```bash
cd 1-GPT/p_90
mvn clean package
mvn spring-boot:run
```

## API

### Create short URL
`POST /api/shorten`

Request body:
```json
{ "destinationUrl": "https://example.com/docs", "ttlMinutes": 120 }
```

Response:
```json
{
  "shortCode": "Ab12XyZ",
  "shortLink": "/Ab12XyZ",
  "expiresAt": "2024-06-01T15:30:00Z"
}
```

### Redirect
`GET /api/{code}` — Responds with HTTP 302 redirect if active, otherwise 404 with JSON error.

### Details / Analytics
`GET /api/info/{code}` — Returns destination, creation/expiration timestamps, click count, and recent click events.

## Notes
- TTL is optional; omit `ttlMinutes` for non-expiring links.
- MongoDB collection `short_urls` automatically stores indexes for quick lookup.

## Stop
Press `Ctrl+C` in the terminal to stop the Spring Boot application.
