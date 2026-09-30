# URL Shortener API

This project is a URL shortener API with analytics, built with Express and MongoDB.

## Requirements

- Node.js
- npm
- MongoDB

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Make sure you have a MongoDB server running.

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

### API Endpoints

-   `POST /shorten`: Shorten a URL.

    **Request Body:**

    ```json
    {
        "originalUrl": "https://www.google.com",
        "expiresAt": "2025-12-31T23:59:59.000Z" // Optional
    }
    ```

-   `GET /:shortUrl`: Redirect to the original URL.

-   `GET /analytics/:shortUrl`: Get analytics for a shortened URL.
