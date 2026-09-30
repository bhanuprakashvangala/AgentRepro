package com.example.redis.cache.service;

import com.example.redis.cache.config.CacheProperties;
import java.time.Duration;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class RedisCacheService {

    private static final Logger logger = LoggerFactory.getLogger(RedisCacheService.class);

    private final StringRedisTemplate redisTemplate;
    private final CacheProperties properties;

    public RedisCacheService(StringRedisTemplate redisTemplate, CacheProperties properties) {
        this.redisTemplate = redisTemplate;
        this.properties = properties;
    }

    public void set(String key, String value) {
        set(key, value, Duration.ofSeconds(properties.getDefaultTtlSeconds()));
    }

    public void set(String key, String value, Duration ttl) {
        Objects.requireNonNull(key, "key must not be null");
        Objects.requireNonNull(value, "value must not be null");
        Duration effectiveTtl = ttl == null || ttl.isZero() || ttl.isNegative()
                ? Duration.ofSeconds(properties.getDefaultTtlSeconds())
                : ttl;
        redisTemplate.opsForValue().set(key, value, effectiveTtl);
        recordAccess(key);
        enforceEvictionPolicy();
        logger.debug("Set key={} ttl={}s", key, effectiveTtl.toSeconds());
    }

    public Optional<String> get(String key) {
        String value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            recordAccess(key);
        }
        return Optional.ofNullable(value);
    }

    public boolean delete(String key) {
        redisTemplate.opsForZSet().remove(properties.getEvictionSetKey(), key);
        Boolean result = redisTemplate.delete(key);
        return Boolean.TRUE.equals(result);
    }

    public void clearAll() {
        var trackedKeys = redisTemplate.opsForZSet()
                .range(properties.getEvictionSetKey(), 0, -1);
        if (trackedKeys != null && !trackedKeys.isEmpty()) {
            redisTemplate.delete(trackedKeys);
        }
        redisTemplate.delete(properties.getEvictionSetKey());
    }

    public Long ttl(String key) {
        return redisTemplate.getExpire(key);
    }

    private void recordAccess(String key) {
        redisTemplate.opsForZSet()
                .add(properties.getEvictionSetKey(), key, (double) Instant.now().toEpochMilli());
    }

    private void enforceEvictionPolicy() {
        Long size = redisTemplate.opsForZSet().size(properties.getEvictionSetKey());
        if (size == null || size <= properties.getMaxEntries()) {
            return;
        }
        long excess = size - properties.getMaxEntries();
        logger.debug("Eviction policy triggered: {} excess entries", excess);
        var keysToEvict = redisTemplate.opsForZSet()
                .range(properties.getEvictionSetKey(), 0, excess - 1);
        if (keysToEvict == null || keysToEvict.isEmpty()) {
            return;
        }
        redisTemplate.delete(keysToEvict);
        redisTemplate.opsForZSet().remove(properties.getEvictionSetKey(), keysToEvict.toArray());
    }
}
