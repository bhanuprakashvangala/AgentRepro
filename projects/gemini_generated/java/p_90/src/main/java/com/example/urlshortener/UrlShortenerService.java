package com.example.urlshortener;

import com.google.common.hash.Hashing;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class UrlShortenerService {

    private final UrlMappingRepository urlMappingRepository;

    @Autowired
    public UrlShortenerService(UrlMappingRepository urlMappingRepository) {
        this.urlMappingRepository = urlMappingRepository;
    }

    public String shortenUrl(String originalUrl, LocalDateTime expirationDate) {
        String shortUrl = Hashing.murmur3_32_fixed().hashString(originalUrl, StandardCharsets.UTF_8).toString();
        UrlMapping urlMapping = new UrlMapping(originalUrl, shortUrl, expirationDate);
        urlMappingRepository.save(urlMapping);
        return shortUrl;
    }

    public Optional<UrlMapping> getOriginalUrl(String shortUrl) {
        Optional<UrlMapping> urlMappingOptional = urlMappingRepository.findByShortUrl(shortUrl);
        if (urlMappingOptional.isPresent()) {
            UrlMapping urlMapping = urlMappingOptional.get();
            if (urlMapping.getExpirationDate() != null && urlMapping.getExpirationDate().isBefore(LocalDateTime.now())) {
                urlMappingRepository.delete(urlMapping);
                return Optional.empty();
            }
            urlMapping.setClickCount(urlMapping.getClickCount() + 1);
            urlMapping.setLastAccessedDate(LocalDateTime.now());
            urlMappingRepository.save(urlMapping);
        }
        return urlMappingOptional;
    }

    @Scheduled(fixedRate = 3600000) // Run every hour
    public void deleteExpiredUrls() {
        List<UrlMapping> expiredUrls = urlMappingRepository.findByExpirationDateBefore(LocalDateTime.now());
        urlMappingRepository.deleteAll(expiredUrls);
    }
}
