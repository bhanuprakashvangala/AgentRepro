# Data Validation Service with Hibernate Validator

This project demonstrates how to use Hibernate Validator in a Spring Boot application to validate DTOs and define custom validation constraints.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd data-validation-service
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

You can create a user by sending a POST request to `http://localhost:8080/users` with a JSON body.

**Example using cURL (Valid Request):**

```bash
curl -X POST -H "Content-Type: application/json" -d '
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "Password123"
}' http://localhost:8080/users
```

**Successful Response:**

```
User created successfully
```

**Example using cURL (Invalid Request):**

```bash
curl -X POST -H "Content-Type: application/json" -d '
{
  "name": "J",
  "email": "not-an-email",
  "password": "pass"
}' http://localhost:8080/users
```

**Error Response:**

```json
{
  "password": "Invalid password",
  "name": "Name must be between 2 and 30 characters",
  "email": "Email should be valid"
}
```
