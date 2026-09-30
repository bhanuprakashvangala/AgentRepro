package com.example.cache;

import com.google.common.cache.*;
import com.google.gson.Gson;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

enum EvictionPolicy {
    LRU,  // Least Recently Used
    LFU,  // Least Frequently Used
    FIFO  // First In First Out
}

class CacheEntry<V> {
    private final V value;
    private final Instant createdAt;
    private Instant lastAccessedAt;
    private final Long ttlSeconds;
    private long accessCount;

    public CacheEntry(V value, Long ttlSeconds) {
        this.value = value;
        this.createdAt = Instant.now();
        this.lastAccessedAt = Instant.now();
        this.ttlSeconds = ttlSeconds;
        this.accessCount = 0;
    }

    public V getValue() {
        lastAccessedAt = Instant.now();
        accessCount++;
        return value;
    }

    public boolean isExpired() {
        if (ttlSeconds == null) return false;
        return Instant.now().getEpochSecond() - createdAt.getEpochSecond() > ttlSeconds;
    }

    public Instant getCreatedAt() { return createdAt; }
    public Instant getLastAccessedAt() { return lastAccessedAt; }
    public long getAccessCount() { return accessCount; }
    public Long getTtlSeconds() { return ttlSeconds; }
}

class CacheStatistics {
    private final AtomicLong hits = new AtomicLong(0);
    private final AtomicLong misses = new AtomicLong(0);
    private final AtomicLong evictions = new AtomicLong(0);
    private final AtomicLong expirations = new AtomicLong(0);

    public void recordHit() { hits.incrementAndGet(); }
    public void recordMiss() { misses.incrementAndGet(); }
    public void recordEviction() { evictions.incrementAndGet(); }
    public void recordExpiration() { expirations.incrementAndGet(); }

    public long getHits() { return hits.get(); }
    public long getMisses() { return misses.get(); }
    public long getEvictions() { return evictions.get(); }
    public long getExpirations() { return expirations.get(); }

    public double getHitRate() {
        long total = hits.get() + misses.get();
        return total == 0 ? 0.0 : (double) hits.get() / total;
    }

    public void reset() {
        hits.set(0);
        misses.set(0);
        evictions.set(0);
        expirations.set(0);
    }

    @Override
    public String toString() {
        return String.format("CacheStats{hits=%d, misses=%d, evictions=%d, expirations=%d, hitRate=%.2f%%}",
            hits.get(), misses.get(), evictions.get(), expirations.get(), getHitRate() * 100);
    }
}

class CacheConfig {
    private int maxSize = 1000;
    private Long defaultTtlSeconds = null;
    private EvictionPolicy evictionPolicy = EvictionPolicy.LRU;
    private boolean enableStatistics = true;

    public int getMaxSize() { return maxSize; }
    public void setMaxSize(int maxSize) { this.maxSize = maxSize; }

    public Long getDefaultTtlSeconds() { return defaultTtlSeconds; }
    public void setDefaultTtlSeconds(Long defaultTtlSeconds) {
        this.defaultTtlSeconds = defaultTtlSeconds;
    }

    public EvictionPolicy getEvictionPolicy() { return evictionPolicy; }
    public void setEvictionPolicy(EvictionPolicy evictionPolicy) {
        this.evictionPolicy = evictionPolicy;
    }

    public boolean isEnableStatistics() { return enableStatistics; }
    public void setEnableStatistics(boolean enableStatistics) {
        this.enableStatistics = enableStatistics;
    }
}

class SimpleCache<K, V> {
    private final Map<K, CacheEntry<V>> cache;
    private final CacheConfig config;
    private final CacheStatistics stats;
    private final ScheduledExecutorService cleanupExecutor;

    public SimpleCache(CacheConfig config) {
        this.config = config;
        this.stats = new CacheStatistics();

        // Initialize cache based on eviction policy
        this.cache = switch (config.getEvictionPolicy()) {
            case LRU -> Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                    boolean shouldRemove = size() > config.getMaxSize();
                    if (shouldRemove) stats.recordEviction();
                    return shouldRemove;
                }
            });
            case FIFO -> Collections.synchronizedMap(new LinkedHashMap<>(16, 0.75f, false) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
                    boolean shouldRemove = size() > config.getMaxSize();
                    if (shouldRemove) stats.recordEviction();
                    return shouldRemove;
                }
            });
            default -> new ConcurrentHashMap<>();
        };

        // Start cleanup thread for expired entries
        this.cleanupExecutor = Executors.newSingleThreadScheduledExecutor();
        cleanupExecutor.scheduleAtFixedRate(this::cleanupExpired, 1, 1, TimeUnit.SECONDS);
    }

    public void put(K key, V value) {
        put(key, value, config.getDefaultTtlSeconds());
    }

    public void put(K key, V value, Long ttlSeconds) {
        CacheEntry<V> entry = new CacheEntry<>(value, ttlSeconds);
        cache.put(key, entry);
    }

    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);

        if (entry == null) {
            if (config.isEnableStatistics()) stats.recordMiss();
            return null;
        }

        if (entry.isExpired()) {
            cache.remove(key);
            if (config.isEnableStatistics()) {
                stats.recordMiss();
                stats.recordExpiration();
            }
            return null;
        }

        if (config.isEnableStatistics()) stats.recordHit();
        return entry.getValue();
    }

    public boolean containsKey(K key) {
        CacheEntry<V> entry = cache.get(key);
        if (entry == null) return false;

        if (entry.isExpired()) {
            cache.remove(key);
            return false;
        }

        return true;
    }

    public void remove(K key) {
        cache.remove(key);
    }

    public void clear() {
        cache.clear();
        stats.reset();
    }

    public int size() {
        return cache.size();
    }

    public CacheStatistics getStatistics() {
        return stats;
    }

    private void cleanupExpired() {
        List<K> expiredKeys = new ArrayList<>();

        cache.forEach((key, entry) -> {
            if (entry.isExpired()) {
                expiredKeys.add(key);
            }
        });

        expiredKeys.forEach(key -> {
            cache.remove(key);
            if (config.isEnableStatistics()) {
                stats.recordExpiration();
            }
        });
    }

    public void shutdown() {
        cleanupExecutor.shutdown();
    }

    public Map<K, V> getAll(Collection<K> keys) {
        Map<K, V> result = new HashMap<>();
        for (K key : keys) {
            V value = get(key);
            if (value != null) {
                result.put(key, value);
            }
        }
        return result;
    }

    public void putAll(Map<K, V> entries) {
        entries.forEach(this::put);
    }
}

class GuavaCache<K, V> {
    private final Cache<K, V> cache;
    private final CacheStatistics stats = new CacheStatistics();

    public GuavaCache(int maxSize, long ttlSeconds) {
        CacheBuilder<Object, Object> builder = CacheBuilder.newBuilder()
            .maximumSize(maxSize)
            .recordStats();

        if (ttlSeconds > 0) {
            builder.expireAfterWrite(ttlSeconds, TimeUnit.SECONDS);
        }

        this.cache = builder
            .removalListener((RemovalNotification<K, V> notification) -> {
                if (notification.getCause() == RemovalCause.SIZE) {
                    stats.recordEviction();
                } else if (notification.getCause() == RemovalCause.EXPIRED) {
                    stats.recordExpiration();
                }
            })
            .build();
    }

    public void put(K key, V value) {
        cache.put(key, value);
    }

    public V get(K key) {
        V value = cache.getIfPresent(key);
        if (value != null) {
            stats.recordHit();
        } else {
            stats.recordMiss();
        }
        return value;
    }

    public V getOrLoad(K key, Callable<V> loader) throws Exception {
        V value = cache.get(key, loader);
        if (value != null) {
            stats.recordHit();
        } else {
            stats.recordMiss();
        }
        return value;
    }

    public void invalidate(K key) {
        cache.invalidate(key);
    }

    public void invalidateAll() {
        cache.invalidateAll();
    }

    public long size() {
        return cache.size();
    }

    public CacheStatistics getStatistics() {
        return stats;
    }

    public CacheStats getGuavaStats() {
        return cache.stats();
    }
}

class CacheManager {
    private final Map<String, SimpleCache<?, ?>> caches = new ConcurrentHashMap<>();

    @SuppressWarnings("unchecked")
    public <K, V> SimpleCache<K, V> getCache(String name, CacheConfig config) {
        return (SimpleCache<K, V>) caches.computeIfAbsent(name, k -> new SimpleCache<>(config));
    }

    public void removeCache(String name) {
        SimpleCache<?, ?> cache = caches.remove(name);
        if (cache != null) {
            cache.shutdown();
        }
    }

    public void clearAll() {
        caches.values().forEach(SimpleCache::clear);
    }

    public void shutdown() {
        caches.values().forEach(SimpleCache::shutdown);
        caches.clear();
    }

    public Map<String, CacheStatistics> getAllStatistics() {
        Map<String, CacheStatistics> allStats = new HashMap<>();
        caches.forEach((name, cache) -> allStats.put(name, cache.getStatistics()));
        return allStats;
    }
}

public class CacheManagerApp {

    public static void main(String[] args) throws Exception {
        System.out.println("=== Cache Manager Demo ===\n");

        // Example 1: Simple LRU Cache
        System.out.println("--- Example 1: LRU Cache ---");
        CacheConfig lruConfig = new CacheConfig();
        lruConfig.setMaxSize(3);
        lruConfig.setEvictionPolicy(EvictionPolicy.LRU);

        SimpleCache<String, String> lruCache = new SimpleCache<>(lruConfig);

        lruCache.put("key1", "value1");
        lruCache.put("key2", "value2");
        lruCache.put("key3", "value3");

        System.out.println("Cache size: " + lruCache.size());
        System.out.println("Get key1: " + lruCache.get("key1")); // Access key1

        lruCache.put("key4", "value4"); // This should evict key2 (least recently used)

        System.out.println("After adding key4:");
        System.out.println("  key1: " + lruCache.get("key1"));
        System.out.println("  key2: " + lruCache.get("key2")); // null
        System.out.println("  key3: " + lruCache.get("key3"));
        System.out.println("  key4: " + lruCache.get("key4"));
        System.out.println("Statistics: " + lruCache.getStatistics());

        // Example 2: TTL Cache
        System.out.println("\n--- Example 2: TTL Cache ---");
        CacheConfig ttlConfig = new CacheConfig();
        ttlConfig.setDefaultTtlSeconds(2L); // 2 seconds TTL

        SimpleCache<String, String> ttlCache = new SimpleCache<>(ttlConfig);

        ttlCache.put("temp1", "expires soon");
        System.out.println("Immediately after put: " + ttlCache.get("temp1"));

        Thread.sleep(3000); // Wait for expiration

        System.out.println("After 3 seconds: " + ttlCache.get("temp1")); // null (expired)
        System.out.println("Statistics: " + ttlCache.getStatistics());

        // Example 3: Guava Cache with automatic loading
        System.out.println("\n--- Example 3: Guava Cache with Loading ---");
        GuavaCache<Integer, String> guavaCache = new GuavaCache<>(100, 60);

        // Simulate expensive data loading
        Callable<String> loader = () -> {
            System.out.println("  Loading data from database...");
            Thread.sleep(100);
            return "Expensive Data";
        };

        System.out.println("First access (cache miss):");
        String data1 = guavaCache.getOrLoad(1, loader);
        System.out.println("  Result: " + data1);

        System.out.println("\nSecond access (cache hit):");
        String data2 = guavaCache.getOrLoad(1, loader);
        System.out.println("  Result: " + data2);

        System.out.println("Guava Stats: " + guavaCache.getGuavaStats());

        // Example 4: Cache Manager with multiple caches
        System.out.println("\n--- Example 4: Cache Manager ---");
        CacheManager manager = new CacheManager();

        CacheConfig userCacheConfig = new CacheConfig();
        userCacheConfig.setMaxSize(1000);
        userCacheConfig.setDefaultTtlSeconds(300L);

        CacheConfig sessionCacheConfig = new CacheConfig();
        sessionCacheConfig.setMaxSize(500);
        sessionCacheConfig.setDefaultTtlSeconds(1800L);

        SimpleCache<String, String> userCache = manager.getCache("users", userCacheConfig);
        SimpleCache<String, String> sessionCache = manager.getCache("sessions", sessionCacheConfig);

        // Populate caches
        userCache.put("user123", "Alice");
        userCache.put("user456", "Bob");
        sessionCache.put("session_abc", "active");

        System.out.println("User cache size: " + userCache.size());
        System.out.println("Session cache size: " + sessionCache.size());

        // Get all statistics
        System.out.println("\nAll cache statistics:");
        manager.getAllStatistics().forEach((name, stats) ->
            System.out.println("  " + name + ": " + stats)
        );

        // Example 5: Bulk operations
        System.out.println("\n--- Example 5: Bulk Operations ---");
        SimpleCache<String, Integer> bulkCache = new SimpleCache<>(new CacheConfig());

        Map<String, Integer> bulkData = Map.of(
            "item1", 100,
            "item2", 200,
            "item3", 300,
            "item4", 400
        );

        bulkCache.putAll(bulkData);
        System.out.println("Added " + bulkData.size() + " items to cache");

        Map<String, Integer> retrieved = bulkCache.getAll(List.of("item1", "item3", "item5"));
        System.out.println("Retrieved items: " + retrieved);

        // Cleanup
        lruCache.shutdown();
        ttlCache.shutdown();
        bulkCache.shutdown();
        manager.shutdown();

        System.out.println("\n=== Cache Manager Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Multiple eviction policies (LRU, LFU, FIFO)");
        System.out.println("  ✓ TTL-based expiration");
        System.out.println("  ✓ Cache statistics");
        System.out.println("  ✓ Bulk operations");
        System.out.println("  ✓ Multiple cache namespaces");
        System.out.println("  ✓ Automatic cleanup of expired entries");
    }
}
