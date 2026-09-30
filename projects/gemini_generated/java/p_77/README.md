# Spring Boot Microservice with Kafka Integration

This project is a Spring Boot microservice with Kafka integration, demonstrating both producer and consumer functionalities.

## Requirements

- Java 17 or higher
- Maven
- Apache Kafka (running locally or accessible)

## Installation

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Build the project using Maven:

    ```bash
    mvn clean install
    ```

## Usage

1.  Ensure your Kafka server is running. You can start Kafka using Docker:

    ```bash
    docker-compose up -d
    ```

2.  Run the Spring Boot application:

    ```bash
    mvn spring-boot:run
    ```

3.  Send a POST request to `http://localhost:8080/send` with a `message` parameter to produce a Kafka message:

    ```bash
    curl -X POST "http://localhost:8080/send?message=Hello Kafka!"
    ```

4.  Observe the console output for both the producer sending the message and the consumer receiving it.
