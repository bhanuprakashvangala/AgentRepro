package com.example.uploadservice.model;

import java.time.Instant;

public record FileMetadata(
        String fileName,
        String contentType,
        long size,
        Instant uploadedAt,
        String path
) {
}
