package com.example.auth.controller;

import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class ProtectedController {

    @GetMapping("/greeting")
    public Map<String, String> greet(Authentication authentication) {
        return Map.of(
                "message", "Hello " + authentication.getName(),
                "roles", authentication.getAuthorities().toString()
        );
    }
}
