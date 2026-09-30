package com.example.healthcheck;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component
public class ExternalServiceHealthIndicator implements HealthIndicator {

    @Override
    public Health health() {
        try {
            // Simulate checking an external service
            boolean isServiceUp = checkExternalService();

            if (isServiceUp) {
                return Health.up().withDetail("externalService", "Available").build();
            } else {
                return Health.down().withDetail("externalService", "Not Available").build();
            }
        } catch (Exception e) {
            return Health.down(e).withDetail("externalService", "Error").build();
        }
    }

    private boolean checkExternalService() {
        // In a real application, this would involve making an actual call to an external service
        // For demonstration purposes, we'll always return true
        return true;
    }
}
