# API Versioning System for REST Endpoints

This project demonstrates different API versioning strategies (URL-based and Header-based) in a Spring Boot application, along with deprecated version warnings and API documentation using Springdoc OpenAPI (Swagger).

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd api-versioning
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

### URL-Based Versioning

- **Access V1 User API:**
  ```bash
  curl -v http://localhost:8080/v1/users
  ```
  You should see a `X-API-WARN` header in the response indicating that `/v1` is deprecated.

- **Access V2 User API:**
  ```bash
  curl http://localhost:8080/v2/users
  ```

### Header-Based Versioning

- **Access V1 Product API:**
  ```bash
  curl -H "Accept: application/vnd.api.v1+json" http://localhost:8080/products
  ```

- **Access V2 Product API:**
  ```bash
  curl -H "Accept: application/vnd.api.v2+json" http://localhost:8080/products
  ```

### API Documentation (Swagger UI)

Access the Swagger UI at `http://localhost:8080/swagger-ui.html` to explore the API endpoints and their versions.
