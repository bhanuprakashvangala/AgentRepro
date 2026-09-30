# Database Connection Pool Manager with HikariCP

This project demonstrates a database connection pool manager using Spring Boot and HikariCP.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd connection-pool-manager
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

### Get All Users

```bash
curl http://localhost:8080/users
```

### Add a User

```bash
curl -X POST "http://localhost:8080/users?name=Alice"
```

### Monitor Connection Pool

Spring Boot Actuator provides endpoints to monitor the connection pool. You can access them at:

- `http://localhost:8080/actuator/health`
- `http://localhost:8080/actuator/metrics`
- `http://localhost:8080/actuator/metrics/hikaricp.connections`

### H2 Console

The H2 console is enabled for easy database inspection. You can access it at `http://localhost:8080/h2-console`.

- **JDBC URL:** `jdbc:h2:mem:testdb`
- **User Name:** `sa`
- **Password:** `password`
