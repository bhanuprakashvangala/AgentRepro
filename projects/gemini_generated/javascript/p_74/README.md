# JWT Token Manager with Refresh Tokens

This project is a JWT token manager with refresh tokens, built with Express and jsonwebtoken.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your JWT secrets:

    ```
    ACCESS_TOKEN_SECRET=your_access_token_secret
    REFRESH_TOKEN_SECRET=your_refresh_token_secret
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

### API Endpoints

-   `POST /login`: Authenticate and get access and refresh tokens.

    **Request Body:**

    ```json
    {
        "username": "testuser"
    }
    ```

-   `POST /token`: Refresh an access token using a refresh token.

    **Request Body:**

    ```json
    {
        "token": "<refresh-token>"
    }
    ```

-   `DELETE /logout`: Invalidate a refresh token.

    **Request Body:**

    ```json
    {
        "token": "<refresh-token>"
    }
    ```

-   `GET /protected`: A protected route that requires a valid access token.

    **Headers:**

    ```
    Authorization: Bearer <access-token>
    ```
