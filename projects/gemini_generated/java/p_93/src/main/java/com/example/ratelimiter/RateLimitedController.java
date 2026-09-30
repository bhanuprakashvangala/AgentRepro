package com.example.ratelimiter;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class RateLimitedController {

    @GetMapping("/rate-limited")
    public ResponseEntity<String> rateLimitedEndpoint() {
        return ResponseEntity.ok("This is a rate-limited endpoint!");
    }

    @GetMapping("/unlimited")
    public ResponseEntity<String> unlimitedEndpoint() {
        return ResponseEntity.ok("This is an unlimited endpoint!");
    }
}
