package com.example.ratelimiter.service;

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import io.github.bucket4j.BucketConfiguration;
import io.github.bucket4j.Refill;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class RateLimiterService {

    private final Map<String, Bucket> bucketCache = new ConcurrentHashMap<>();

    private final BucketConfiguration configuration;

    public RateLimiterService(
            @Value("${ratelimiter.capacity:10}") long capacity,
            @Value("${ratelimiter.refill.tokens:10}") long refillTokens,
            @Value("${ratelimiter.refill.period-seconds:60}") long periodSeconds
    ) {
        Bandwidth limit = Bandwidth.classic(capacity, Refill.intervally(refillTokens, Duration.ofSeconds(periodSeconds)));
        this.configuration = BucketConfiguration.builder().addLimit(limit).build();
    }

    public boolean tryConsume(String clientId) {
        Bucket bucket = bucketCache.computeIfAbsent(clientId, this::newBucket);
        return bucket.tryConsume(1);
    }

    private Bucket newBucket(String key) {
        return Bucket.builder().applyConfiguration(configuration).build();
    }
}
