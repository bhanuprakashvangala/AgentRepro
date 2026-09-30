import json
import functools
import hashlib
from typing import Any, Callable, Optional, Union
import redis
from datetime import timedelta


class RedisCache:
    """Redis-based caching layer with TTL and invalidation support."""

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True
    ):
        """
        Initialize Redis connection.

        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            decode_responses: Whether to decode responses to strings
        """
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses
        )

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a unique cache key based on function name and arguments.

        Args:
            prefix: Key prefix (usually function name)
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Unique cache key
        """
        # Create a string representation of all arguments
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        # Hash it to keep keys manageable
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.client.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            print(f"Cache get error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds or as timedelta

        Returns:
            True if successful, False otherwise
        """
        try:
            serialized_value = json.dumps(value)
            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                return bool(self.client.setex(key, ttl, serialized_value))
            else:
                return bool(self.client.set(key, serialized_value))
        except (redis.RedisError, json.JSONEncodeError, TypeError) as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            print(f"Cache delete error: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "cache:my_function:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = list(self.client.scan_iter(match=pattern))
            if keys:
                return self.client.delete(*keys)
            return 0
        except redis.RedisError as e:
            print(f"Cache invalidation error: {e}")
            return 0

    def clear_all(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.flushdb()
            return True
        except redis.RedisError as e:
            print(f"Cache clear error: {e}")
            return False

    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            print(f"Cache TTL error: {e}")
            return None


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cache(
    ttl: Optional[Union[int, timedelta]] = 300,
    key_prefix: Optional[str] = None
):
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time-to-live in seconds or as timedelta (default: 300 seconds)
        key_prefix: Custom key prefix (default: function name)

    Example:
        @cache(ttl=600)
        def get_user(user_id):
            return expensive_database_query(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_client = get_cache()
            prefix = key_prefix or func.__name__
            cache_key = cache_client._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache_client.get(cache_key)
            if cached_value is not None:
                print(f"Cache HIT: {prefix}")
                return cached_value

            # Cache miss - call function
            print(f"Cache MISS: {prefix}")
            result = func(*args, **kwargs)

            # Store in cache
            cache_client.set(cache_key, result, ttl)

            return result

        # Add invalidation method to function
        def invalidate(*args, **kwargs):
            """Invalidate cache for specific arguments."""
            cache_client = get_cache()
            prefix = key_prefix or func.__name__
            cache_key = cache_client._generate_key(prefix, *args, **kwargs)
            return cache_client.delete(cache_key)

        def invalidate_all():
            """Invalidate all cache entries for this function."""
            cache_client = get_cache()
            prefix = key_prefix or func.__name__
            pattern = f"cache:{prefix}:*"
            return cache_client.invalidate_pattern(pattern)

        wrapper.invalidate = invalidate
        wrapper.invalidate_all = invalidate_all

        return wrapper
    return decorator


def invalidate_cache(func_name: str, *args, **kwargs) -> bool:
    """
    Manually invalidate cache for a specific function call.

    Args:
        func_name: Name of the cached function
        *args: Arguments passed to the function
        **kwargs: Keyword arguments passed to the function

    Returns:
        True if cache was invalidated, False otherwise
    """
    cache_client = get_cache()
    cache_key = cache_client._generate_key(func_name, *args, **kwargs)
    return cache_client.delete(cache_key)


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache entries matching a pattern.

    Args:
        pattern: Pattern to match (e.g., "cache:get_user:*")

    Returns:
        Number of cache entries invalidated
    """
    cache_client = get_cache()
    return cache_client.invalidate_pattern(pattern)


# Example usage
if __name__ == "__main__":
    import time

    # Example function
    @cache(ttl=60)
    def expensive_calculation(x: int, y: int) -> int:
        """Simulate expensive calculation."""
        print(f"Computing {x} + {y}...")
        time.sleep(2)
        return x + y

    print("Testing Redis cache...")

    # First call - cache miss
    result1 = expensive_calculation(10, 20)
    print(f"Result: {result1}\n")

    # Second call - cache hit
    result2 = expensive_calculation(10, 20)
    print(f"Result: {result2}\n")

    # Invalidate cache
    print("Invalidating cache...")
    expensive_calculation.invalidate(10, 20)

    # Third call - cache miss again
    result3 = expensive_calculation(10, 20)
    print(f"Result: {result3}")
