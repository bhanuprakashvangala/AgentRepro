# Notification System with RabbitMQ

This project demonstrates a simple notification system using Spring Boot and RabbitMQ.

## Requirements

- Java 8 or higher
- Maven
- RabbitMQ server running locally (or accessible via `localhost:5672`)

## How to Run

1. **Start RabbitMQ Server:**
   Ensure you have a RabbitMQ server running. You can run it using Docker:
   ```bash
   docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

2. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd notification-system
   ```

3. **Build the project:**
   ```bash
   mvn clean install
   ```

4. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start, and the `NotificationReceiver` will start listening for messages.

## Usage

You can send notifications by sending a POST request to `http://localhost:8080/send-notification` with a JSON body.

**Example using cURL:**

```bash
curl -X POST -H "Content-Type: application/json" -d '
{
  "recipient": "user@example.com",
  "message": "Hello from RabbitMQ!"
}' http://localhost:8080/send-notification
```

Upon sending the request, you will see output in the console indicating that the notification was sent and received.
