package com.example.health.indicator;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component("externalService")
public class ExternalServiceHealthIndicator implements HealthIndicator {

    private static final Logger logger = LoggerFactory.getLogger(ExternalServiceHealthIndicator.class);

    private final HttpClient client;
    private final URI uri;
    private final Duration timeout;

    public ExternalServiceHealthIndicator(
            @Value("${health.external.url:https://example.com}") String url,
            @Value("${health.external.timeout-seconds:2}") long timeoutSeconds) {
        this.uri = URI.create(url);
        this.timeout = Duration.ofSeconds(Math.max(timeoutSeconds, 1));
        this.client = HttpClient.newBuilder()
                .connectTimeout(this.timeout)
                .build();
    }

    @Override
    public Health health() {
        HttpRequest request = HttpRequest.newBuilder(uri)
                .method("HEAD", HttpRequest.BodyPublishers.noBody())
                .timeout(timeout)
                .build();
        try {
            HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
            int status = response.statusCode();
            if (status >= 200 && status < 300) {
                return Health.up().withDetail("url", uri.toString()).withDetail("status", status).build();
            }
            return Health.down().withDetail("url", uri.toString()).withDetail("status", status).build();
        } catch (IOException | InterruptedException ex) {
            logger.warn("External service health check failed", ex);
            return Health.down(ex).withDetail("url", uri.toString()).build();
        }
    }
}
