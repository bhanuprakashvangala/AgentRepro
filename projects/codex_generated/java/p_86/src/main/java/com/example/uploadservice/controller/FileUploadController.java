package com.example.uploadservice.controller;

import com.example.uploadservice.model.FileMetadata;
import com.example.uploadservice.service.FileStorageService;
import org.apache.commons.fileupload.FileUploadException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import jakarta.servlet.http.HttpServletRequest;
import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/files")
public class FileUploadController {

    private final FileStorageService storageService;

    public FileUploadController(FileStorageService storageService) {
        this.storageService = storageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> upload(HttpServletRequest request) throws IOException, FileUploadException {
        FileMetadata metadata = storageService.handleUpload(request);
        return ResponseEntity.ok(Map.of(
                "status", "uploaded",
                "fileName", metadata.fileName(),
                "contentType", metadata.contentType(),
                "size", metadata.size(),
                "uploadedAt", metadata.uploadedAt(),
                "path", metadata.path()
        ));
    }
}
