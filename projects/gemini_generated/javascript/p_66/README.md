# Proxy Server

This project is a proxy server with request logging, built with Express and http-proxy-middleware.

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

2.  The proxy server will be running at `http://localhost:3000`.

3.  Any request to the proxy server will be forwarded to `http://httpbin.org`.

### Features

-   **Request Logging**: All incoming requests are logged to the console.
-   **Header Manipulation**: A custom header `X-Special-Proxy-Header` is added to the request, and the `x-powered-by` header is removed from the response.
-   **CORS Handling**: The `Access-Control-Allow-Origin` header is set to `*` in the response.
