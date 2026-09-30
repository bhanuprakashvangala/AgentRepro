# Log Aggregator Service

This project is a log aggregator service built with Winston.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the logger:

    ```bash
    npm start
    ```

2.  The logger will generate logs to the console, a daily rotating file in the `logs` directory, and send logs to an HTTP endpoint.

### Transports

-   **Console**: Logs are output to the console.
-   **File**: Logs are written to a daily rotating file in the `logs` directory. The files are rotated hourly, compressed, and kept for 14 days.
-   **HTTP**: Logs are sent to an HTTP endpoint at `http://localhost:8080/logs`.
