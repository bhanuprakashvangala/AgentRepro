# Spring Boot REST API with JPA and MySQL

This project is a Spring Boot REST API for user management with JPA and MySQL.

## Requirements

- Java 17 or higher
- Maven
- MySQL database

## Database Setup

1.  Create a MySQL database named `mydatabase`.
2.  Create a user `myuser` with password `mypassword` and grant all privileges to `mydatabase`.

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

-   `GET /users`: Get all users.
-   `GET /users/{id}`: Get a user by ID.
-   `POST /users`: Create a new user.
-   `PUT /users/{id}`: Update a user by ID.
-   `DELETE /users/{id}`: Delete a user by ID.

### Example Request (POST /users)

```json
{
    "name": "John Doe",
    "email": "john.doe@example.com"
}
```
