package com.example.redis.cache.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.redis")
public record RedisSettings(
        String host,
        int port,
        String password
) {
    public RedisSettings {
        if (host == null || host.isBlank()) {
            host = "localhost";
        }
        if (port <= 0) {
            port = 6379;
        }
    }
}
