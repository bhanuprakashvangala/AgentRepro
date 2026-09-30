package com.example.urlshortener.controller;

import com.example.urlshortener.model.ShortUrl;
import com.example.urlshortener.service.ShortUrlService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.time.Duration;
import java.util.Map;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.view.RedirectView;

@RestController
@RequestMapping("/api")
@Validated
public class UrlController {

    private final ShortUrlService shortUrlService;

    public UrlController(ShortUrlService shortUrlService) {
        this.shortUrlService = shortUrlService;
    }

    @PostMapping("/shorten")
    public ResponseEntity<Map<String, Object>> shorten(@RequestBody @Validated ShortenRequest request) {
        Duration ttl = request.getTtlMinutes() == null ? null : Duration.ofMinutes(request.getTtlMinutes());
        ShortUrl shortUrl = shortUrlService.createShortUrl(request.getDestinationUrl(), ttl);
        String shortLink = "/" + shortUrl.getShortCode();
        return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "shortCode", shortUrl.getShortCode(),
                "shortLink", shortLink,
                "expiresAt", shortUrl.getExpiresAt()
        ));
    }

    @GetMapping("/info/{code}")
    public ResponseEntity<?> info(@PathVariable("code") String code) {
        return shortUrlService.getDetails(code)
                .map(url -> ResponseEntity.ok(Map.of(
                        "destination", url.getDestinationUrl(),
                        "createdAt", url.getCreatedAt(),
                        "expiresAt", url.getExpiresAt(),
                        "clickCount", url.getClickCount(),
                        "recentClicks", url.getClickEvents()
                )))
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Short code not found")));
    }

    @GetMapping("/{code}")
    public ResponseEntity<?> redirect(@PathVariable("code") String code, HttpServletRequest request) {
        return shortUrlService.resolveShortCode(code, request.getHeader(HttpHeaders.USER_AGENT), request.getRemoteAddr())
                .map(url -> ResponseEntity.status(HttpStatus.FOUND)
                        .header(HttpHeaders.LOCATION, url.getDestinationUrl())
                        .build())
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Short code not found or expired")));
    }

    public static class ShortenRequest {

        @NotBlank(message = "Destination URL is required")
        private String destinationUrl;

        @Min(value = 1, message = "TTL must be at least 1 minute")
        private Long ttlMinutes;

        public String getDestinationUrl() {
            return destinationUrl;
        }

        public void setDestinationUrl(String destinationUrl) {
            this.destinationUrl = destinationUrl;
        }

        public Long getTtlMinutes() {
            return ttlMinutes;
        }

        public void setTtlMinutes(Long ttlMinutes) {
            this.ttlMinutes = ttlMinutes;
        }
    }
}
