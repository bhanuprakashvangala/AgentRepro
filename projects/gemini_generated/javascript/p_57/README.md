# Webhook Receiver and Processor

This project is a webhook receiver and processor built with Express.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

2.  Create a `.env` file in the root directory and add your webhook secret:

    ```
    WEBHOOK_SECRET=my-super-secret-key
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Send a POST request to `http://localhost:3000/webhook` with a JSON payload.

### Webhook Validation

The webhook receiver validates the signature of incoming webhooks. The signature should be passed in the `x-hub-signature-256` header. The signature is a SHA256 HMAC of the request body, using the webhook secret as the key.

### Asynchronous Processing

Webhook events are added to an in-memory queue and processed asynchronously every 5 seconds.
