# Redis API Cache Layer

Provides decorator-based caching for Python functions (e.g., API calls) using Redis as the backend. Includes TTL support and cache invalidation helpers.

## Prerequisites
- Running Redis server (default connection `redis://localhost:6379/0`).  
  Adjust via `REDIS_URL` environment variable if needed.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
### 1. Start Redis
```bash
redis-server
```

### 2. Run the example
```bash
python app.py
```
This script calls `agify.io` to predict ages for random names, caching responses for 120 seconds. It then invalidates the namespace and fetches again to demonstrate a cache miss.

### 3. Integrate in your code
```python
from redis_cache import cache, invalidate

@cache(ttl=300, namespace="weather")
def fetch_weather(city):
    ...  # expensive API call

# Invalidate
invalidate(namespace="weather")
```

- `cache(ttl, namespace)` decorator caches JSON-serializable results for the specified TTL.
- `invalidate(namespace=..., key=...)` removes cached entries.
- Default TTL is 300 seconds if not specified.

## Configuration
Set environment variables before running:
```bash
export REDIS_URL="redis://:password@redis-host:6379/1"
```

The caching layer serializes inputs/outputs to JSON, making it easy to cache API responses and other serializable data structures.
