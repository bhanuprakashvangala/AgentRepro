# Elasticsearch Search Service

Spring Boot REST API using Spring Data Elasticsearch. Allows indexing article documents, running full-text search, filtering by tags/author, and paginating results.

## Features
- Spring Data Elasticsearch integration (8.x compatible)
- `ArticleDocument` mapping with text, keyword, and date fields
- Full-text search across title/body via multi-match query
- Filtering by tags (terms) and author (exact match)
- Pagination and sorting (published date by default)

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- Elasticsearch 8.x running locally (default URI `http://localhost:9200`)
  - Ensure `elasticsearch.username/password` in `application.properties` if security is enabled (defaults assume none)

## Build & Run
```bash
cd 1-GPT/p_91
mvn clean package
mvn spring-boot:run
```

## API

### Index Article
`POST /api/articles`

```json
{
  "title": "Intro to Elasticsearch",
  "body": "Elasticsearch lets you search everything...",
  "tags": ["search", "elasticsearch"],
  "author": "Jamie",
  "readTimeMinutes": 7
}
```

Response `201 Created` with stored document (including generated ID, publishedAt).

### Search
`GET /api/articles?q=search&tags=elasticsearch&author=Jamie&page=0&size=5`

Returns JSON with `totalHits`, `totalPages`, pagination info, and `content` containing search hits.

Parameters:
- `q` – full-text query (optional; defaults to match all)
- `tags` – comma-separated or repeated query parameter (e.g., `tags=dev&tags=java`)
- `author` – exact author filter
- `page`, `size` – pagination (defaults 0, 10)
- `sort` & `direction` – sorting options (defaults to `publishedAt` desc)

## Notes
- Ensure the `articles` index exists; Spring Data will create mapping automatically on first save.
- For secured clusters, provide credentials via `spring.elasticsearch.username/password`.

## Stop
Use `Ctrl+C` to terminate the Spring Boot app.
