package com.example.rediscacheexample;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/cache")
public class CacheController {

    @Autowired
    private CacheService cacheService;

    @PostMapping("/{key}")
    public void set(@PathVariable String key, @RequestBody Object value, @RequestParam long ttl) {
        cacheService.set(key, value, ttl);
    }

    @GetMapping("/{key}")
    public Object get(@PathVariable String key) {
        return cacheService.get(key);
    }

    @DeleteMapping("/{key}")
    public void delete(@PathVariable String key) {
        cacheService.delete(key);
    }
}