package com.example.health.controller;

import com.zaxxer.hikari.HikariDataSource;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthEndpoint;
import org.springframework.boot.actuate.metrics.MetricsEndpoint;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final HealthEndpoint healthEndpoint;
    private final MetricsEndpoint metricsEndpoint;
    private final DataSource dataSource;

    public HealthController(HealthEndpoint healthEndpoint, MetricsEndpoint metricsEndpoint, DataSource dataSource) {
        this.healthEndpoint = healthEndpoint;
        this.metricsEndpoint = metricsEndpoint;
        this.dataSource = dataSource;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Health health = healthEndpoint.health();
        Map<String, Object> body = new HashMap<>();
        body.put("status", health.getStatus());
        body.put("components", health.getDetails());

        Map<String, Object> metrics = new HashMap<>();
        MetricsEndpoint.MetricResponse uptime = metricsEndpoint.metric("process.uptime", null);
        if (uptime != null && uptime.getMeasurements().size() > 0) {
            metrics.put("process.uptime", uptime.getMeasurements().get(0).getValue());
        }

        if (dataSource instanceof HikariDataSource hikari) {
            Map<String, Object> pool = new HashMap<>();
            pool.put("total", hikari.getHikariPoolMXBean().getTotalConnections());
            pool.put("active", hikari.getHikariPoolMXBean().getActiveConnections());
            pool.put("idle", hikari.getHikariPoolMXBean().getIdleConnections());
            pool.put("threadsAwaiting", hikari.getHikariPoolMXBean().getThreadsAwaitingConnection());
            metrics.put("connectionPool", pool);
        }

        body.put("metrics", metrics);
        return ResponseEntity.ok(body);
    }
}
