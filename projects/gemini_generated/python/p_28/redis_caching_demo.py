import redis
import time
import json
from functools import wraps

# --- Redis Connection ---
# This script assumes a Redis server is running on localhost:6379
try:
    redis_client = redis.Redis(host='localhost', port=6379)
    # Check the connection
    redis_client.ping()
    print("Successfully connected to Redis.")
except redis.exceptions.ConnectionError as e:
    print("[ERROR] Could not connect to Redis. Please ensure it is running on localhost:6379.")
    print(f"Details: {e}")
    exit()

# --- Helper function to create a cache key ---
def _make_cache_key(func, *args, **kwargs) -> str:
    # Create a stable key based on function name, args, and kwargs
    key_parts = [func.__name__] + list(args) + sorted(kwargs.items())
    return ":".join(map(str, key_parts))

# --- Cache Decorator ---
def cache(ttl: int):
    """
    A decorator to cache the results of a function in Redis with a TTL.
    Handles serialization of Python objects to JSON.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_cache_key(func, *args, **kwargs)
            print(f"\n{'='*20}\nAttempting to fetch from cache with key: '{key}'")
            
            # Try to get from cache first
            cached_value = redis_client.get(key)
            if cached_value:
                print("[CACHE HIT]")
                # Deserialize from JSON string
                return json.loads(cached_value.decode('utf-8'))
            
            # If cache miss, execute the function
            print("[CACHE MISS]")
            result = func(*args, **kwargs)
            
            # Serialize to JSON string and set in Redis with TTL
            serialized_result = json.dumps(result)
            redis_client.set(key, serialized_result, ex=ttl)
            print(f"Result cached in Redis with a TTL of {ttl} seconds.")
            
            return result
        return wrapper
    return decorator

# --- Cache Invalidation Function ---
def invalidate_cache(func, *args, **kwargs):
    """Manually invalidates/deletes a cache entry for a function."""
    key_to_invalidate = _make_cache_key(func, *args, **kwargs)
    print(f"\n[INVALIDATING] Deleting cache for key: '{key_to_invalidate}'")
    redis_client.delete(key_to_invalidate)

# --- Demo Function ---
@cache(ttl=10) # Cache results for 10 seconds
def slow_api_call(user_id: str) -> dict:
    """A simulated slow API call that we want to cache."""
    print(f"Executing slow API call for {user_id}... (will take 2 seconds)")
    time.sleep(2)
    return {"user_id": user_id, "data": "some_user_data", "timestamp": time.time()}

if __name__ == "__main__":
    print("\n--- Caching Demonstration ---")
    
    # 1. First call is a CACHE MISS (slow)
    print("1. First call for user '123'")
    slow_api_call(user_id='123')

    # 2. Second call is a CACHE HIT (fast)
    print("\n2. Second call for user '123' within TTL")
    slow_api_call(user_id='123')

    # 3. Wait for TTL to expire
    print("\n3. Waiting for 11 seconds for the cache to expire...")
    time.sleep(11)

    # 4. Third call is a CACHE MISS again (slow)
    print("4. Third call for user '123' after TTL has expired")
    slow_api_call(user_id='123')

    print("\n--- Invalidation Demonstration ---")
    
    # 5. First call is a CACHE MISS (slow)
    print("5. First call for user '789'")
    slow_api_call(user_id='789')

    # 6. Manually invalidate the cache
    print("\n6. Manually invalidating the cache for user '789'")
    invalidate_cache(slow_api_call, user_id='789')
    
    # 7. Second call is a CACHE MISS again because it was invalidated (slow)
    print("\n7. Second call for user '789' after invalidation")
    slow_api_call(user_id='789')
    
    print("\n--- DEMO COMPLETE ---")
