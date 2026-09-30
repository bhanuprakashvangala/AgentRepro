# Distributed Cache with Redis Cluster

This project demonstrates a distributed cache using Redis Cluster with the `ioredis` library.

## Requirements

- Node.js
- npm
- A running Redis Cluster (e.g., 3 master nodes on ports 7000, 7001, 7002).

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Ensure your Redis Cluster is running and accessible on the specified ports (7000, 7001, 7002).

2.  Run the cache operations script:

    ```bash
    npm start
    ```

### Operations

-   **Set with TTL**: A key `mykey` is set with a value `myvalue` and a TTL of 10 seconds.
-   **Get**: The value of `mykey` is retrieved at different intervals to demonstrate TTL.
-   **Failover**: `ioredis` automatically handles failover if a node in the cluster becomes unavailable.
