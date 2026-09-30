# CSV to Database Importer

Spring Boot application that reads CSV files with headers using Apache Commons CSV and performs JDBC batch inserts into an H2 database.

## Features
- Apache Commons CSV parsing with header awareness
- JDBC batch insert (100 rows per batch) into `persons` table
- Robust error handling: skips bad records, rolls back on batch failure
- REST endpoint to trigger import by pointing to a file path
- Sample CSV (`src/main/resources/data/sample.csv`) and schema auto-loaded into in-memory H2

## Prerequisites
- Java 17+
- Apache Maven 3.9+

## Build & Run
```bash
cd 1-GPT/p_96
mvn clean package
mvn spring-boot:run
```

## Trigger Import
```bash
curl -X POST "http://localhost:8080/api/import?path=src/main/resources/data/sample.csv"
```

Response example:
```
Imported 3 records from src/main/resources/data/sample.csv
```

Errors during parsing are logged and the offending record is skipped. Fatal errors cause the import to roll back.

## Stop
Use `Ctrl+C` to stop the application.
