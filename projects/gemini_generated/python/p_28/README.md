# Redis-Based Caching Layer

This project demonstrates a simple but powerful Redis-based caching layer in Python, implemented as a decorator.

## ⚠️ CRITICAL: External Dependency

This script requires a **Redis server to be installed and running** on your local machine at its default port (`localhost:6379`).

- **To install Redis**, follow the official instructions on the Redis website: [https://redis.io/docs/getting-started/](https://redis.io/docs/getting-started/)

The script will show a connection error and exit if it cannot find a running Redis instance.

## Features

- **Cache Decorator**: A `@cache(ttl=...)` decorator that can be applied to any function to automatically cache its results.
- **Time-to-Live (TTL)**: Cache entries automatically expire after the specified number of seconds.
- **Serialization**: Handles Python objects (like dictionaries) by serializing them to JSON before caching.
- **Cache Invalidation**: Includes a `invalidate_cache()` function to manually delete a specific cached result.
- **Clear Demonstration**: The script runs a step-by-step demo showing cache misses, hits, TTL expiration, and manual invalidation.

## Usage

1.  **Install and run Redis**: Make sure your Redis server is running.

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the script:**
    ```bash
    python redis_caching_demo.py
    ```

## Expected Output

You will see a series of print statements walking you through the demonstration. Observe the `[CACHE HIT]` and `[CACHE MISS]` messages and the delays caused by the simulated `slow_api_call` to understand how the caching layer is working.

```
Successfully connected to Redis.

--- Caching Demonstration ---
1. First call for user '123'

====================
Attempting to fetch from cache with key: 'slow_api_call:user_id=123'
[CACHE MISS]
Executing slow API call for user_id=123... (will take 2 seconds)
Result cached in Redis with a TTL of 10 seconds.

2. Second call for user '123' within TTL

====================
Attempting to fetch from cache with key: 'slow_api_call:user_id=123'
[CACHE HIT]

3. Waiting for 11 seconds for the cache to expire...
...
```
