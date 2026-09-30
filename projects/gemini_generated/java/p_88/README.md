# Logging Framework with Log4j2

This project demonstrates how to configure and use Log4j2 in a Spring Boot application.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd logging-framework
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start, log messages to the console, and write them to files in the `logs` directory.

## Log Files

- **`logs/app.log`**: This file contains all log messages.
- **`logs/rolling-app.log`**: This file also contains all log messages, but it will be rotated when it reaches 1 KB. The old log files will be renamed to `logs/rolling-app-1.log`, `logs/rolling-app-2.log`, and so on.

## Log Levels

The `log4j2.xml` file is configured to log messages with level `trace` and higher for the `com.example.logging` package. You can change the log levels in the `log4j2.xml` file to control the amount of logging.
