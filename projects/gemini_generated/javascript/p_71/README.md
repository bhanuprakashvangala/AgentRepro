# Data Validation Middleware with Joi

This project is a data validation middleware with Joi, built with Express.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Send a POST request to `http://localhost:3000/users` with a JSON payload.

### Example Valid Request Body

```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 30,
    "password": "password123"
}
```

### Example Invalid Request Body

```json
{
    "name": "Jo",
    "email": "invalid-email",
    "age": 17,
    "password": "abc"
}
```

If the request body is invalid, the API will return a `400 Bad Request` status code with detailed error messages.
