#!/usr/bin/env python3
"""Redis-based caching utilities for API responses."""

from __future__ import annotations

import functools
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

import redis

F = TypeVar("F", bound=Callable[..., Any])

_DEFAULT_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@dataclass
class CacheConfig:
    redis_url: str = _DEFAULT_REDIS_URL
    default_ttl: int = 300
    namespace: str = "cache"


class RedisCache:
    """Simple Redis-backed cache with decorator helpers."""

    def __init__(self, config: CacheConfig | None = None) -> None:
        self.config = config or CacheConfig()
        self._client_lock = threading.Lock()
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            with self._client_lock:
                if self._client is None:
                    self._client = redis.from_url(self.config.redis_url, decode_responses=True)
        return self._client

    def make_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}" if namespace else key

    def get(self, key: str, namespace: Optional[str] = None) -> Optional[str]:
        full_key = self.make_key(namespace or self.config.namespace, key)
        return self.client.get(full_key)

    def set(self, key: str, value: str, ttl: Optional[int] = None, namespace: Optional[str] = None) -> None:
        full_key = self.make_key(namespace or self.config.namespace, key)
        self.client.set(full_key, value, ex=ttl if ttl is not None else self.config.default_ttl)

    def delete(self, key: str, namespace: Optional[str] = None) -> int:
        full_key = self.make_key(namespace or self.config.namespace, key)
        return self.client.delete(full_key)

    def invalidate_namespace(self, namespace: str) -> int:
        pattern = f"{namespace}:*"
        keys = self.client.keys(pattern)
        if not keys:
            return 0
        return self.client.delete(*keys)

    def cache(self, ttl: Optional[int] = None, namespace: Optional[str] = None) -> Callable[[F], F]:
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                key = self._serialize_call(func.__name__, args, kwargs)
                cached = self.get(key, namespace)
                if cached is not None:
                    return json.loads(cached)
                result = func(*args, **kwargs)
                self.set(key, json.dumps(result, default=self._json_default), ttl=ttl, namespace=namespace)
                return result

            return wrapper  # type: ignore[return-value]

        return decorator

    def _serialize_call(self, func_name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
        payload = {
            "func": func_name,
            "args": args,
            "kwargs": kwargs,
        }
        return json.dumps(payload, sort_keys=True, default=self._json_default)

    def _json_default(self, obj: Any) -> str:
        if isinstance(obj, (set, tuple)):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="ignore")
        if isinstance(obj, time.struct_time):
            return time.strftime("%Y-%m-%dT%H:%M:%S", obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


# Example usage decorator
_cache_instance: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cache(ttl: Optional[int] = None, namespace: Optional[str] = None) -> Callable[[F], F]:
    return get_cache().cache(ttl=ttl, namespace=namespace)


def invalidate(namespace: Optional[str] = None, key: Optional[str] = None) -> int:
    cache_instance = get_cache()
    if key:
        return cache_instance.delete(key, namespace)
    if namespace:
        return cache_instance.invalidate_namespace(namespace)
    raise ValueError("Either namespace or key must be provided for invalidation")
