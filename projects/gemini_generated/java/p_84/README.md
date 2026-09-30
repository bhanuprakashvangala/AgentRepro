# Spring Mail Example

This is a simple Spring Boot application that demonstrates how to send emails with Thymeleaf templates and attachments.

## Prerequisites

- A Mailtrap account (or any other SMTP server).
- Update the `application.properties` file with your SMTP server credentials.

## Usage

1. Build the project:
   ```
   mvn clean install
   ```
2. Run the application:
   ```
   java -jar target/spring-mail-example-1.0-SNAPSHOT.jar
   ```

### API

- `POST /send-email?to=<recipient>&subject=<subject>&name=<name>`: Send an email.
