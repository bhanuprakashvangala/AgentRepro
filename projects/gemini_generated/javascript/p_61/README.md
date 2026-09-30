# Job Queue Processor with Bull

This project is a job queue processor built with Bull and Redis.

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

1.  Start the consumer to process jobs:

    ```bash
    npm run start:consumer
    ```

2.  In a separate terminal, start the producer to add jobs to the queue:

    ```bash
    npm run start:producer
    ```

### Job Processing

-   The consumer will process jobs from the queue.
-   Jobs have a retry logic of 3 attempts with a 5-second backoff.
-   The consumer will randomly fail jobs to demonstrate the retry logic.
