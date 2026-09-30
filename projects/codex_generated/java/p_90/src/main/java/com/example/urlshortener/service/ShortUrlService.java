package com.example.urlshortener.service;

import com.example.urlshortener.model.ShortUrl;
import com.example.urlshortener.model.ShortUrl.ClickEvent;
import com.example.urlshortener.repository.ShortUrlRepository;
import java.net.URI;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class ShortUrlService {

    private static final Logger logger = LoggerFactory.getLogger(ShortUrlService.class);
    private static final int DEFAULT_CODE_LENGTH = 7;

    private final ShortUrlRepository repository;

    public ShortUrlService(ShortUrlRepository repository) {
        this.repository = repository;
    }

    public ShortUrl createShortUrl(String destinationUrl, Duration ttl) {
        validateUrl(destinationUrl);
        ShortUrl shortUrl = new ShortUrl();
        shortUrl.setDestinationUrl(destinationUrl);
        shortUrl.setCreatedAt(Instant.now());
        if (ttl != null && !ttl.isNegative() && !ttl.isZero()) {
            shortUrl.setExpiresAt(shortUrl.getCreatedAt().plus(ttl));
        }
        shortUrl.setShortCode(generateUniqueCode());
        ShortUrl saved = repository.save(shortUrl);
        logger.info("Created short URL {} -> {}", saved.getShortCode(), saved.getDestinationUrl());
        return saved;
    }

    public Optional<ShortUrl> resolveShortCode(String shortCode, String userAgent, String ipAddress) {
        return repository.findByShortCode(shortCode)
                .filter(this::notExpired)
                .map(url -> recordClick(url, userAgent, ipAddress));
    }

    public Optional<ShortUrl> getDetails(String shortCode) {
        return repository.findByShortCode(shortCode);
    }

    private ShortUrl recordClick(ShortUrl shortUrl, String userAgent, String ipAddress) {
        shortUrl.setClickCount(shortUrl.getClickCount() + 1);
        ClickEvent event = new ClickEvent();
        event.setUserAgent(StringUtils.hasText(userAgent) ? userAgent : "unknown");
        event.setIpAddress(StringUtils.hasText(ipAddress) ? ipAddress : "unknown");
        shortUrl.getClickEvents().add(event);
        repository.save(shortUrl);
        return shortUrl;
    }

    private boolean notExpired(ShortUrl shortUrl) {
        Instant expiresAt = shortUrl.getExpiresAt();
        if (expiresAt == null) {
            return true;
        }
        boolean active = Instant.now().isBefore(expiresAt);
        if (!active) {
            logger.info("Short URL {} expired at {}", shortUrl.getShortCode(), expiresAt);
        }
        return active;
    }

    private String generateUniqueCode() {
        for (int attempt = 0; attempt < 5; attempt++) {
            String candidate = RandomStringUtils.randomAlphanumeric(DEFAULT_CODE_LENGTH);
            if (repository.findByShortCode(candidate).isEmpty()) {
                return candidate;
            }
        }
        return UUID.randomUUID().toString().replaceAll("-", "").substring(0, DEFAULT_CODE_LENGTH + 1);
    }

    private void validateUrl(String destinationUrl) {
        try {
            URI uri = URI.create(destinationUrl);
            if (!uri.isAbsolute()) {
                throw new IllegalArgumentException("Destination URL must be absolute");
            }
        } catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("Invalid destination URL", ex);
        }
    }
}
