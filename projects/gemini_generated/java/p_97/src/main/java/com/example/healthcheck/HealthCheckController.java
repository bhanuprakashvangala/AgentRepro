package com.example.healthcheck;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthCheckController {

    @GetMapping("/")
    public ResponseEntity<String> home() {
        return ResponseEntity.ok("Health Check Application is running. Access /actuator/health for health status.");
    }
}
