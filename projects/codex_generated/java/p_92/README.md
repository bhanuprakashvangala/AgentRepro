# RabbitMQ Notification Service

Spring Boot application that publishes notification messages to RabbitMQ and consumes them with manual acknowledgments.

## Features
- Spring AMQP integration with RabbitMQ topic exchange and durable queue
- REST endpoint to submit notifications
- Publisher confirms enabled on the connection factory
- Listener uses manual ack (`basicAck` / `basicNack`) to guarantee processing
- Dead-letter exchange/queue configuration for failed messages

## Prerequisites
- Java 17+
- Apache Maven 3.9+
- RabbitMQ server running (default: `amqp://guest:guest@localhost:5672`)

## Configure
Adjust `src/main/resources/application.properties` for host/credentials if needed.

## Build & Run
```bash
cd 1-GPT/p_92
mvn clean package
mvn spring-boot:run
```

## Publish Notification
```bash
curl -X POST http://localhost:8080/api/notifications \
  -H "Content-Type: application/json" \
  -d '{
        "recipient": "alice@example.com",
        "subject": "Welcome",
        "body": "Thanks for signing up!"
      }'
```

Response:
```json
{ "status": "queued", "recipient": "alice@example.com" }
```

The `NotificationListener` logs processing, acks on success, and nacks without requeue on failure (sending to DLQ).

## Stop
Press `Ctrl+C` in the terminal running Spring Boot.
