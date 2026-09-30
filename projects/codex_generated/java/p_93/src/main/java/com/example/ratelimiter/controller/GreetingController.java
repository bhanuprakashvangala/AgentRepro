package com.example.ratelimiter.controller;

import jakarta.validation.constraints.NotBlank;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Validated
public class GreetingController {

    @GetMapping("/api/greet")
    public ResponseEntity<String> greet(@RequestParam(defaultValue = "World") @NotBlank String name) {
        return ResponseEntity.ok("Hello, " + name + "!");
    }
}
