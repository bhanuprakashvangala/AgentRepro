# Spring Batch CSV → Database Demo

Reads `input/persons.csv`, processes records in chunks, and writes valid entries to an in-memory H2 database. Demonstrates retry/skip logic using Spring Batch.

## Requirements
- Java 17+
- Maven

## Run
```bash
mvn spring-boot:run
```
The job launches automatically. Check logs for chunk processing, retry/skip messages, and saved entities.

Connect to H2 console (optional):
```
JDBC URL: jdbc:h2:mem:batchdb
User: sa
Password: (blank)
```
Query `SELECT * FROM PEOPLE;` to view persisted rows.

Records with negative age trigger retries (up to 3) and are eventually skipped (skip limit 5). Modify `input/persons.csv` and relaunch for new runs.
