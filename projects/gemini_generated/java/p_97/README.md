# Health Check Endpoint for Spring Boot

This project demonstrates how to build a health check endpoint for a Spring Boot application using Spring Boot Actuator.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd health-check
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

Once the application is running, you can access the health check endpoints:

- **Overall Health Status:**
  ```bash
  curl http://localhost:8080/actuator/health
  ```
  This will return a JSON response indicating the overall health status of the application, including database connectivity and the custom external service check.

- **Metrics:**
  ```bash
  curl http://localhost:8080/actuator/metrics
  ```
  This will list available metrics.

- **Specific Metric (e.g., JVM memory usage):**
  ```bash
  curl http://localhost:8080/actuator/metrics/jvm.memory.used
  ```

- **Application Info:**
  ```bash
  curl http://localhost:8080/actuator/info
  ```

- **H2 Console:**
  The H2 console is enabled for easy database inspection. You can access it at `http://localhost:8080/h2-console`.

  - **JDBC URL:** `jdbc:h2:mem:testdb`
  - **User Name:** `sa`
  - **Password:** `password`
