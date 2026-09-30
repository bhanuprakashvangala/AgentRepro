package com.example.redis.cache.controller;

import com.example.redis.cache.model.CacheEntryRequest;
import com.example.redis.cache.model.CacheEntryResponse;
import com.example.redis.cache.service.RedisCacheService;
import jakarta.validation.Valid;
import java.time.Duration;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/cache")
public class CacheController {

    private final RedisCacheService cacheService;

    public CacheController(RedisCacheService cacheService) {
        this.cacheService = cacheService;
    }

    @GetMapping("/{key}")
    public ResponseEntity<CacheEntryResponse> get(@PathVariable String key) {
        return cacheService.get(key)
                .map(value -> new CacheEntryResponse(key, value, cacheService.ttl(key)))
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<CacheEntryResponse> set(@RequestBody @Valid CacheEntryRequest request) {
        Duration ttl = request.getTtlSeconds() != null ? Duration.ofSeconds(request.getTtlSeconds()) : null;
        if (ttl != null) {
            cacheService.set(request.getKey(), request.getValue(), ttl);
        } else {
            cacheService.set(request.getKey(), request.getValue());
        }
        return ResponseEntity.ok(new CacheEntryResponse(
                request.getKey(),
                request.getValue(),
                cacheService.ttl(request.getKey())
        ));
    }

    @DeleteMapping("/{key}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable String key) {
        boolean removed = cacheService.delete(key);
        return ResponseEntity.ok(Map.of(
                "key", key,
                "removed", removed
        ));
    }
}
