# Session Management with Redis

This project is a session management system with Redis, built with Express, express-session, and connect-redis.

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

2.  Open your browser and go to `http://localhost:3000`.

3.  Refresh the page to see the session view count increase.

4.  Go to `http://localhost:3000/regenerate` to regenerate the session.

### Session Configuration

-   Sessions are stored in Redis.
-   Sessions expire after 10 minutes.
-   The session cookie is `httpOnly` and `secure` (if using HTTPS).
