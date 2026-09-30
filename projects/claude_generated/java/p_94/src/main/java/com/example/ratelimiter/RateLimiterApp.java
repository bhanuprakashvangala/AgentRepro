package com.example.ratelimiter;

import com.google.common.util.concurrent.RateLimiter;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

interface IRateLimiter {
    boolean tryAcquire();
    boolean tryAcquire(int permits);
    void acquire();
    void acquire(int permits);
    void reset();
    RateLimitStats getStats();
}

class RateLimitStats {
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong allowedRequests = new AtomicLong(0);
    private final AtomicLong deniedRequests = new AtomicLong(0);

    public void recordAllowed() {
        totalRequests.incrementAndGet();
        allowedRequests.incrementAndGet();
    }

    public void recordDenied() {
        totalRequests.incrementAndGet();
        deniedRequests.incrementAndGet();
    }

    public long getTotalRequests() { return totalRequests.get(); }
    public long getAllowedRequests() { return allowedRequests.get(); }
    public long getDeniedRequests() { return deniedRequests.get(); }

    public double getAllowRate() {
        long total = totalRequests.get();
        return total == 0 ? 1.0 : (double) allowedRequests.get() / total;
    }

    public void reset() {
        totalRequests.set(0);
        allowedRequests.set(0);
        deniedRequests.set(0);
    }

    @Override
    public String toString() {
        return String.format("Stats{total=%d, allowed=%d, denied=%d, allowRate=%.2f%%}",
            getTotalRequests(), getAllowedRequests(), getDeniedRequests(), getAllowRate() * 100);
    }
}

// Token Bucket Rate Limiter
class TokenBucketRateLimiter implements IRateLimiter {
    private final int capacity;
    private final int refillRate; // tokens per second
    private int tokens;
    private long lastRefillTime;
    private final RateLimitStats stats;

    public TokenBucketRateLimiter(int capacity, int refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefillTime = System.currentTimeMillis();
        this.stats = new RateLimitStats();
    }

    @Override
    public synchronized boolean tryAcquire() {
        return tryAcquire(1);
    }

    @Override
    public synchronized boolean tryAcquire(int permits) {
        refill();

        if (tokens >= permits) {
            tokens -= permits;
            stats.recordAllowed();
            return true;
        }

        stats.recordDenied();
        return false;
    }

    @Override
    public void acquire() {
        acquire(1);
    }

    @Override
    public void acquire(int permits) {
        while (!tryAcquire(permits)) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    private void refill() {
        long now = System.currentTimeMillis();
        long elapsedSeconds = (now - lastRefillTime) / 1000;

        if (elapsedSeconds > 0) {
            int tokensToAdd = (int) (elapsedSeconds * refillRate);
            tokens = Math.min(capacity, tokens + tokensToAdd);
            lastRefillTime = now;
        }
    }

    @Override
    public synchronized void reset() {
        tokens = capacity;
        lastRefillTime = System.currentTimeMillis();
        stats.reset();
    }

    @Override
    public RateLimitStats getStats() {
        return stats;
    }
}

// Fixed Window Rate Limiter
class FixedWindowRateLimiter implements IRateLimiter {
    private final int maxRequests;
    private final long windowSizeMs;
    private int requestCount;
    private long windowStart;
    private final RateLimitStats stats;

    public FixedWindowRateLimiter(int maxRequests, long windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSizeMs = windowSizeMs;
        this.requestCount = 0;
        this.windowStart = System.currentTimeMillis();
        this.stats = new RateLimitStats();
    }

    @Override
    public synchronized boolean tryAcquire() {
        return tryAcquire(1);
    }

    @Override
    public synchronized boolean tryAcquire(int permits) {
        long now = System.currentTimeMillis();

        // Check if we need to reset the window
        if (now - windowStart >= windowSizeMs) {
            requestCount = 0;
            windowStart = now;
        }

        if (requestCount + permits <= maxRequests) {
            requestCount += permits;
            stats.recordAllowed();
            return true;
        }

        stats.recordDenied();
        return false;
    }

    @Override
    public void acquire() {
        acquire(1);
    }

    @Override
    public void acquire(int permits) {
        while (!tryAcquire(permits)) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    @Override
    public synchronized void reset() {
        requestCount = 0;
        windowStart = System.currentTimeMillis();
        stats.reset();
    }

    @Override
    public RateLimitStats getStats() {
        return stats;
    }
}

// Sliding Window Rate Limiter
class SlidingWindowRateLimiter implements IRateLimiter {
    private final int maxRequests;
    private final long windowSizeMs;
    private final Queue<Long> requestTimestamps;
    private final RateLimitStats stats;

    public SlidingWindowRateLimiter(int maxRequests, long windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSizeMs = windowSizeMs;
        this.requestTimestamps = new ConcurrentLinkedQueue<>();
        this.stats = new RateLimitStats();
    }

    @Override
    public synchronized boolean tryAcquire() {
        return tryAcquire(1);
    }

    @Override
    public synchronized boolean tryAcquire(int permits) {
        long now = System.currentTimeMillis();
        long cutoff = now - windowSizeMs;

        // Remove expired timestamps
        while (!requestTimestamps.isEmpty() && requestTimestamps.peek() < cutoff) {
            requestTimestamps.poll();
        }

        if (requestTimestamps.size() + permits <= maxRequests) {
            for (int i = 0; i < permits; i++) {
                requestTimestamps.offer(now);
            }
            stats.recordAllowed();
            return true;
        }

        stats.recordDenied();
        return false;
    }

    @Override
    public void acquire() {
        acquire(1);
    }

    @Override
    public void acquire(int permits) {
        while (!tryAcquire(permits)) {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    @Override
    public synchronized void reset() {
        requestTimestamps.clear();
        stats.reset();
    }

    @Override
    public RateLimitStats getStats() {
        return stats;
    }
}

// Guava-based Rate Limiter
class GuavaRateLimiter implements IRateLimiter {
    private final RateLimiter rateLimiter;
    private final RateLimitStats stats;

    public GuavaRateLimiter(double permitsPerSecond) {
        this.rateLimiter = RateLimiter.create(permitsPerSecond);
        this.stats = new RateLimitStats();
    }

    @Override
    public boolean tryAcquire() {
        boolean acquired = rateLimiter.tryAcquire();
        if (acquired) {
            stats.recordAllowed();
        } else {
            stats.recordDenied();
        }
        return acquired;
    }

    @Override
    public boolean tryAcquire(int permits) {
        boolean acquired = rateLimiter.tryAcquire(permits);
        if (acquired) {
            stats.recordAllowed();
        } else {
            stats.recordDenied();
        }
        return acquired;
    }

    @Override
    public void acquire() {
        rateLimiter.acquire();
        stats.recordAllowed();
    }

    @Override
    public void acquire(int permits) {
        rateLimiter.acquire(permits);
        stats.recordAllowed();
    }

    @Override
    public void reset() {
        stats.reset();
    }

    @Override
    public RateLimitStats getStats() {
        return stats;
    }
}

// Per-User Rate Limiter
class UserRateLimiter {
    private final Map<String, IRateLimiter> limiters = new ConcurrentHashMap<>();
    private final int maxRequests;
    private final long windowSizeMs;

    public UserRateLimiter(int maxRequests, long windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSizeMs = windowSizeMs;
    }

    public boolean tryAcquire(String userId) {
        IRateLimiter limiter = limiters.computeIfAbsent(userId,
            k -> new SlidingWindowRateLimiter(maxRequests, windowSizeMs));
        return limiter.tryAcquire();
    }

    public RateLimitStats getStats(String userId) {
        IRateLimiter limiter = limiters.get(userId);
        return limiter != null ? limiter.getStats() : new RateLimitStats();
    }

    public Map<String, RateLimitStats> getAllStats() {
        Map<String, RateLimitStats> allStats = new HashMap<>();
        limiters.forEach((userId, limiter) -> allStats.put(userId, limiter.getStats()));
        return allStats;
    }

    public void reset(String userId) {
        IRateLimiter limiter = limiters.get(userId);
        if (limiter != null) {
            limiter.reset();
        }
    }

    public void resetAll() {
        limiters.values().forEach(IRateLimiter::reset);
    }
}

// Rate Limiter with Backoff
class BackoffRateLimiter {
    private final IRateLimiter rateLimiter;
    private final int maxRetries;
    private final long initialBackoffMs;

    public BackoffRateLimiter(IRateLimiter rateLimiter, int maxRetries, long initialBackoffMs) {
        this.rateLimiter = rateLimiter;
        this.maxRetries = maxRetries;
        this.initialBackoffMs = initialBackoffMs;
    }

    public boolean tryAcquireWithBackoff() {
        long backoffMs = initialBackoffMs;

        for (int attempt = 0; attempt < maxRetries; attempt++) {
            if (rateLimiter.tryAcquire()) {
                return true;
            }

            try {
                Thread.sleep(backoffMs);
                backoffMs *= 2; // Exponential backoff
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }

        return false;
    }
}

public class RateLimiterApp {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== Rate Limiter Demo ===\n");

        // Example 1: Token Bucket Rate Limiter
        System.out.println("--- Example 1: Token Bucket (10 requests, 2/sec refill) ---");
        TokenBucketRateLimiter tokenBucket = new TokenBucketRateLimiter(10, 2);

        // Burst of requests
        for (int i = 0; i < 15; i++) {
            boolean allowed = tokenBucket.tryAcquire();
            System.out.println("Request " + (i + 1) + ": " + (allowed ? "ALLOWED" : "DENIED"));
        }
        System.out.println(tokenBucket.getStats());

        // Wait for refill
        Thread.sleep(2000);
        System.out.println("\nAfter 2 seconds (4 tokens refilled):");
        for (int i = 0; i < 6; i++) {
            boolean allowed = tokenBucket.tryAcquire();
            System.out.println("Request " + (i + 1) + ": " + (allowed ? "ALLOWED" : "DENIED"));
        }

        // Example 2: Fixed Window Rate Limiter
        System.out.println("\n--- Example 2: Fixed Window (5 requests per 1 second) ---");
        FixedWindowRateLimiter fixedWindow = new FixedWindowRateLimiter(5, 1000);

        for (int i = 0; i < 8; i++) {
            boolean allowed = fixedWindow.tryAcquire();
            System.out.println("Request " + (i + 1) + ": " + (allowed ? "ALLOWED" : "DENIED"));
            Thread.sleep(100);
        }
        System.out.println(fixedWindow.getStats());

        // Example 3: Sliding Window Rate Limiter
        System.out.println("\n--- Example 3: Sliding Window (5 requests per 1 second) ---");
        SlidingWindowRateLimiter slidingWindow = new SlidingWindowRateLimiter(5, 1000);

        for (int i = 0; i < 8; i++) {
            boolean allowed = slidingWindow.tryAcquire();
            System.out.println("Request " + (i + 1) + " at " +
                System.currentTimeMillis() % 10000 + "ms: " + (allowed ? "ALLOWED" : "DENIED"));
            Thread.sleep(150);
        }
        System.out.println(slidingWindow.getStats());

        // Example 4: Guava Rate Limiter
        System.out.println("\n--- Example 4: Guava Rate Limiter (3 permits/sec) ---");
        GuavaRateLimiter guavaLimiter = new GuavaRateLimiter(3.0);

        long startTime = System.currentTimeMillis();
        for (int i = 0; i < 10; i++) {
            guavaLimiter.acquire(); // Blocks until permit is available
            long elapsed = System.currentTimeMillis() - startTime;
            System.out.println("Request " + (i + 1) + " acquired at " + elapsed + "ms");
        }

        // Example 5: Per-User Rate Limiting
        System.out.println("\n--- Example 5: Per-User Rate Limiting (3 req/sec per user) ---");
        UserRateLimiter userLimiter = new UserRateLimiter(3, 1000);

        String[] users = {"user1", "user2", "user3"};

        for (int round = 0; round < 5; round++) {
            for (String user : users) {
                boolean allowed = userLimiter.tryAcquire(user);
                System.out.println(user + " request " + (round + 1) + ": " +
                    (allowed ? "ALLOWED" : "DENIED"));
            }
            Thread.sleep(200);
        }

        System.out.println("\nPer-user statistics:");
        userLimiter.getAllStats().forEach((user, stats) ->
            System.out.println("  " + user + ": " + stats)
        );

        // Example 6: Rate Limiter with Exponential Backoff
        System.out.println("\n--- Example 6: Rate Limiter with Backoff ---");
        TokenBucketRateLimiter strictLimiter = new TokenBucketRateLimiter(2, 1);
        BackoffRateLimiter backoffLimiter = new BackoffRateLimiter(strictLimiter, 3, 100);

        // Exhaust permits
        strictLimiter.tryAcquire(2);

        System.out.println("Trying to acquire with backoff (permits exhausted):");
        long backoffStart = System.currentTimeMillis();
        boolean acquired = backoffLimiter.tryAcquireWithBackoff();
        long backoffDuration = System.currentTimeMillis() - backoffStart;

        System.out.println("Acquired: " + acquired);
        System.out.println("Backoff duration: " + backoffDuration + "ms");

        // Example 7: Bulk Permits
        System.out.println("\n--- Example 7: Bulk Permit Acquisition ---");
        TokenBucketRateLimiter bulkLimiter = new TokenBucketRateLimiter(20, 5);

        System.out.println("Acquiring 5 permits at once:");
        boolean bulk1 = bulkLimiter.tryAcquire(5);
        System.out.println("  Bulk request 1: " + (bulk1 ? "ALLOWED" : "DENIED"));

        System.out.println("Acquiring 10 permits:");
        boolean bulk2 = bulkLimiter.tryAcquire(10);
        System.out.println("  Bulk request 2: " + (bulk2 ? "ALLOWED" : "DENIED"));

        System.out.println("Acquiring 10 more permits:");
        boolean bulk3 = bulkLimiter.tryAcquire(10);
        System.out.println("  Bulk request 3: " + (bulk3 ? "ALLOWED" : "DENIED"));

        System.out.println(bulkLimiter.getStats());

        System.out.println("\n=== Rate Limiter Demo Complete ===");
        System.out.println("\nImplemented Algorithms:");
        System.out.println("  ✓ Token Bucket (with refill)");
        System.out.println("  ✓ Fixed Window");
        System.out.println("  ✓ Sliding Window");
        System.out.println("  ✓ Guava Rate Limiter");
        System.out.println("\nFeatures:");
        System.out.println("  ✓ Per-user rate limiting");
        System.out.println("  ✓ Bulk permit acquisition");
        System.out.println("  ✓ Exponential backoff");
        System.out.println("  ✓ Rate limit statistics");
        System.out.println("  ✓ Configurable windows and capacities");
    }
}
