package com.example.redis.cache.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.cache")
public class CacheProperties {

    /**
     * Default TTL for cache entries in seconds.
     */
    private long defaultTtlSeconds = 300;

    /**
     * Maximum number of entries allowed in the cache namespace.
     */
    private long maxEntries = 1000;

    /**
     * Redis key for the sorted set that tracks access order.
     */
    private String evictionSetKey = "app:cache:eviction";

    public long getDefaultTtlSeconds() {
        return defaultTtlSeconds;
    }

    public void setDefaultTtlSeconds(long defaultTtlSeconds) {
        this.defaultTtlSeconds = defaultTtlSeconds;
    }

    public long getMaxEntries() {
        return maxEntries;
    }

    public void setMaxEntries(long maxEntries) {
        this.maxEntries = maxEntries;
    }

    public String getEvictionSetKey() {
        return evictionSetKey;
    }

    public void setEvictionSetKey(String evictionSetKey) {
        this.evictionSetKey = evictionSetKey;
    }
}
