# FastAPI JWT Authentication API

This project is a simple REST API built with FastAPI that demonstrates user authentication using JSON Web Tokens (JWT).

## Features

- User registration with secure password hashing (`bcrypt`).
- User login to obtain a JWT.
- A protected route that requires a valid JWT for access.
- Interactive API documentation (via Swagger UI and ReDoc).

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the API server:**
    ```bash
    uvicorn main:app --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

## How to Interact with the API

You can use the interactive documentation by navigating to `http://127.0.0.1:8000/docs` in your browser, or use a tool like `curl`.

### 1. Register a new user

```bash
curl -X POST "http://127.0.0.1:8000/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "password": "testpass"
}'
```

### 2. Log in to get a token

```bash
curl -X POST "http://127.0.0.1:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=testpass"
```

This will return an `access_token`.

### 3. Access the protected route

Replace `YOUR_TOKEN_HERE` with the token you received from the login step.

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
-H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Logout

JWT is stateless. To "log out," the client application should simply delete the token. There is no server-side endpoint for logout.

```
