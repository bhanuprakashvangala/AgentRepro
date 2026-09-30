package com.example.urlshortener;

import org.springframework.data.mongodb.repository.MongoRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface UrlMappingRepository extends MongoRepository<UrlMapping, String> {

    Optional<UrlMapping> findByShortUrl(String shortUrl);

    List<UrlMapping> findByExpirationDateBefore(LocalDateTime date);
}
