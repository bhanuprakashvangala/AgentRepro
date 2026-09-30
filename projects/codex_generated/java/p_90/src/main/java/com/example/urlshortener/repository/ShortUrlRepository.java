package com.example.urlshortener.repository;

import com.example.urlshortener.model.ShortUrl;
import java.util.Optional;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface ShortUrlRepository extends MongoRepository<ShortUrl, String> {

    Optional<ShortUrl> findByShortCode(String shortCode);
}
