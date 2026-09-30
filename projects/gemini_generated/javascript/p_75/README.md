# API Gateway with Routing and Load Balancing

This project is an API gateway with routing and load balancing, built with Express and http-proxy-middleware.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the API Gateway:

    ```bash
    npm start
    ```

2.  The API Gateway will be running on `http://localhost:3000`.

### Microservices

This gateway assumes you have microservices running on the following ports:

-   **Users Service**: `http://localhost:3001`, `http://localhost:3002`
-   **Products Service**: `http://localhost:3003`

### Endpoints

-   `GET /users`: Routes requests to the users microservice with round-robin load balancing.
-   `GET /products`: Routes requests to the products microservice.

### Authentication

All routes require an `Authorization` header with a value of `Bearer mysecrettoken`.

**Example:**

```bash
curl -H "Authorization: Bearer mysecrettoken" http://localhost:3000/users
```
