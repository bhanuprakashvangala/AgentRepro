# Health Check Endpoint

This project is a health check endpoint for microservices, built with Express.

## Requirements

- Node.js
- npm
- MongoDB (for database connectivity check)

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Make sure you have a MongoDB server running if you want the database check to pass.

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Open your browser and go to `http://localhost:3000/health`.

### Health Check Details

The health check endpoint provides the following information:

-   **Overall Status**: `UP` if all checks pass, `DOWN` otherwise.
-   **Database Connectivity**: Checks if the application can connect to MongoDB.
-   **External Service Availability**: Verifies connectivity to an external service (e.g., Google).
-   **System Metrics**: Includes uptime, memory usage, platform, architecture, and CPU count.
