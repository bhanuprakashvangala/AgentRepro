# Rate Limiter Middleware

This project is a rate limiter middleware for APIs, built with `express-rate-limit` and Redis.

## Requirements

- Node.js
- npm
- Redis

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Make sure you have a Redis server running.

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

### Endpoints

-   `/`: A public endpoint with a general rate limit of 100 requests per 15 minutes.
-   `/sensitive`: A sensitive endpoint with a specific rate limit of 10 requests per 5 minutes.

If you exceed the rate limit, you will receive a `429 Too Many Requests` status code.
