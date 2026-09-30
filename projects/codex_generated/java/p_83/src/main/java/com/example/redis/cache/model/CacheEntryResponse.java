package com.example.redis.cache.model;

public record CacheEntryResponse(
        String key,
        String value,
        Long ttlSeconds
) {
}
