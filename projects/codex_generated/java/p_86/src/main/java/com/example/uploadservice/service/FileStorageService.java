package com.example.uploadservice.service;

import com.example.uploadservice.config.StorageProperties;
import com.example.uploadservice.model.FileMetadata;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.Instant;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.fileupload.FileItemIterator;
import org.apache.commons.fileupload.FileItemStream;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.commons.fileupload.util.Streams;
import org.apache.commons.io.FilenameUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.unit.DataSize;

import jakarta.servlet.http.HttpServletRequest;

@Service
public class FileStorageService {

    private static final Logger logger = LoggerFactory.getLogger(FileStorageService.class);

    private final StorageProperties properties;
    private final Path storageDir;
    private final Set<String> allowedContentTypes;

    public FileStorageService(StorageProperties properties) throws IOException {
        this.properties = properties;
        this.storageDir = Path.of(properties.getLocation()).toAbsolutePath().normalize();
        Files.createDirectories(storageDir);
        this.allowedContentTypes = Arrays.stream(properties.getAllowedContentTypes()).collect(Collectors.toSet());
    }

    public FileMetadata handleUpload(HttpServletRequest request) throws IOException, FileUploadException {
        if (!ServletFileUpload.isMultipartContent(request)) {
            throw new IllegalArgumentException("Request is not multipart/form-data");
        }

        ServletFileUpload upload = new ServletFileUpload();
        upload.setFileSizeMax(properties.getMaxFileSize().toBytes());

        FileItemIterator iter = upload.getItemIterator(request);
        while (iter.hasNext()) {
            FileItemStream item = iter.next();
            if (item.isFormField()) {
                // Currently ignoring additional form fields; could be extended later.
                Streams.asString(item.openStream());
                continue;
            }
            return saveFile(item);
        }
        throw new IllegalArgumentException("No file items found in request");
    }

    private FileMetadata saveFile(FileItemStream fileItem) throws IOException {
        String originalName = fileItem.getName();
        String safeFileName = sanitizeFileName(originalName);
        validateFileType(fileItem.getContentType());

        Path targetFile = storageDir.resolve(generateUniqueFileName(safeFileName));
        long size;

        try (InputStream inputStream = fileItem.openStream()) {
            size = Files.copy(inputStream, targetFile, StandardCopyOption.REPLACE_EXISTING);
        }

        DataSize maxSize = properties.getMaxFileSize();
        if (size > maxSize.toBytes()) {
            Files.deleteIfExists(targetFile);
            throw new IllegalArgumentException("File exceeds maximum allowed size of " + maxSize.toMegabytes() + "MB");
        }

        FileMetadata metadata = new FileMetadata(
                targetFile.getFileName().toString(),
                fileItem.getContentType(),
                size,
                Instant.now(),
                targetFile.toString()
        );
        logger.info("Stored file {} ({} bytes)", metadata.fileName(), metadata.size());
        return metadata;
    }

    private void validateFileType(String contentType) {
        if (contentType == null || !allowedContentTypes.contains(contentType)) {
            throw new IllegalArgumentException("Unsupported content type: " + contentType);
        }
    }

    private String sanitizeFileName(String filename) {
        if (filename == null) {
            return "unnamed";
        }
        String baseName = FilenameUtils.getBaseName(filename).replaceAll("[^a-zA-Z0-9-_]", "_");
        String extension = FilenameUtils.getExtension(filename);
        return extension.isBlank() ? baseName : baseName + "." + extension;
    }

    private String generateUniqueFileName(String originalName) {
        String base = FilenameUtils.getBaseName(originalName);
        String ext = FilenameUtils.getExtension(originalName);
        String timestamp = String.valueOf(System.currentTimeMillis());
        return ext.isBlank() ? base + "-" + timestamp : base + "-" + timestamp + "." + ext;
    }
}
