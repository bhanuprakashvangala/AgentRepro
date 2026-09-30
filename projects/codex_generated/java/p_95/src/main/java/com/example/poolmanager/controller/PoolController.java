package com.example.poolmanager.controller;

import com.example.poolmanager.service.HealthCheckService;
import com.zaxxer.hikari.HikariDataSource;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/pool")
public class PoolController {

    private final HikariDataSource dataSource;
    private final HealthCheckService healthCheckService;

    public PoolController(HikariDataSource dataSource, HealthCheckService healthCheckService) {
        this.dataSource = dataSource;
        this.healthCheckService = healthCheckService;
    }

    @GetMapping("/metrics")
    public ResponseEntity<Map<String, Object>> metrics() {
        return ResponseEntity.ok(Map.of(
                "totalConnections", dataSource.getHikariPoolMXBean().getTotalConnections(),
                "activeConnections", dataSource.getHikariPoolMXBean().getActiveConnections(),
                "idleConnections", dataSource.getHikariPoolMXBean().getIdleConnections(),
                "threadsAwaiting", dataSource.getHikariPoolMXBean().getThreadsAwaitingConnection(),
                "health", healthCheckService.checkConnection()
        ));
    }
}
