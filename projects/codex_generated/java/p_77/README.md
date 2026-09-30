# Spring Boot Kafka Microservice

Produces and consumes JSON notifications using Spring Kafka.

## Requirements
- Java 17+
- Maven
- Kafka & Zookeeper running (e.g. via Docker)

```bash
# Example: start cluster
# docker-compose -f docker-compose.kafka.yml up
```

## Configuration
Edit `src/main/resources/application.properties`:
```
app.kafka.bootstrapServers=localhost:9092
app.kafka.topic=notifications
```

## Run
```bash
mvn spring-boot:run
```

## Usage
Send notification:
```bash
curl -X POST http://localhost:8080/api/notifications \
  -H "Content-Type: application/json" \
  -d '{"type":"EMAIL","message":"Hello","createdAt":1690000000000}'
```
Consumer logs consumed messages on the console. Serialization/deserialization handled via JSON, with validation and global exception handling.
