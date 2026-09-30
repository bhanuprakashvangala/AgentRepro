package com.example.redis.cache.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;

public class CacheEntryRequest {

    @NotBlank
    private String key;

    @NotBlank
    private String value;

    @Positive
    private Long ttlSeconds;

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public Long getTtlSeconds() {
        return ttlSeconds;
    }

    public void setTtlSeconds(Long ttlSeconds) {
        this.ttlSeconds = ttlSeconds;
    }
}
