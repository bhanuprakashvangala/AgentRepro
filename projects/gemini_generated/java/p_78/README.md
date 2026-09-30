# JWT Authentication Service with Spring Security

This project is a JWT authentication service built with Spring Boot and Spring Security.

## Requirements

- Java 17 or higher
- Maven

## Installation

1.  Clone the repository.
2.  Navigate to the project directory.
3.  Build the project using Maven:

    ```bash
    mvn clean install
    ```

## Usage

1.  Run the Spring Boot application:

    ```bash
    mvn spring-boot:run
    ```

2.  The API will be available at `http://localhost:8080`.

### API Endpoints

-   `POST /authenticate`: Authenticate and get a JWT token.

    **Request Body:**

    ```json
    {
        "username": "user",
        "password": "password"
    }
    ```

-   `GET /hello`: A protected endpoint that requires a valid JWT token.

    **Headers:**

    ```
    Authorization: Bearer <your-jwt-token>
    ```

### Example Flow

1.  **Authenticate**: Send a POST request to `/authenticate` with username `user` and password `password`. You will receive a JWT token in the response.
2.  **Access Protected Resource**: Use the received JWT token in the `Authorization` header (prefixed with `Bearer `) to access the `/hello` endpoint.
