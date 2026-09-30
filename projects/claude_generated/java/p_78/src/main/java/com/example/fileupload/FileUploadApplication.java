package com.example.fileupload;

import jakarta.persistence.*;
import org.apache.commons.io.FilenameUtils;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@SpringBootApplication
public class FileUploadApplication {
    public static void main(String[] args) {
        SpringApplication.run(FileUploadApplication.class, args);
    }
}

// Entity: FileMetadata
@Entity
@Table(name = "file_metadata")
class FileMetadata {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String storedFilename;

    @Column(nullable = false)
    private String originalFilename;

    @Column(nullable = false)
    private Long fileSize;

    private String contentType;

    @Column(nullable = false)
    private LocalDateTime uploadedAt;

    private String uploadedBy;

    // Constructors
    public FileMetadata() {
        this.uploadedAt = LocalDateTime.now();
    }

    public FileMetadata(String storedFilename, String originalFilename, Long fileSize, String contentType) {
        this();
        this.storedFilename = storedFilename;
        this.originalFilename = originalFilename;
        this.fileSize = fileSize;
        this.contentType = contentType;
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getStoredFilename() { return storedFilename; }
    public void setStoredFilename(String storedFilename) { this.storedFilename = storedFilename; }
    public String getOriginalFilename() { return originalFilename; }
    public void setOriginalFilename(String originalFilename) { this.originalFilename = originalFilename; }
    public Long getFileSize() { return fileSize; }
    public void setFileSize(Long fileSize) { this.fileSize = fileSize; }
    public String getContentType() { return contentType; }
    public void setContentType(String contentType) { this.contentType = contentType; }
    public LocalDateTime getUploadedAt() { return uploadedAt; }
    public void setUploadedAt(LocalDateTime uploadedAt) { this.uploadedAt = uploadedAt; }
    public String getUploadedBy() { return uploadedBy; }
    public void setUploadedBy(String uploadedBy) { this.uploadedBy = uploadedBy; }
}

// Repository
interface FileMetadataRepository extends JpaRepository<FileMetadata, Long> {
    Optional<FileMetadata> findByStoredFilename(String storedFilename);
}

// Custom Exception
class FileStorageException extends RuntimeException {
    public FileStorageException(String message) {
        super(message);
    }
    public FileStorageException(String message, Throwable cause) {
        super(message, cause);
    }
}

// Configuration
@org.springframework.context.annotation.Configuration
class FileStorageConfig {
    public static final String UPLOAD_DIR = "uploads";
    public static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    public static final Set<String> ALLOWED_EXTENSIONS = Set.of("jpg", "jpeg", "png", "pdf", "txt", "doc", "docx");
}

// Service: FileStorageService
@Service
class FileStorageService {
    private final Path uploadPath;
    private final FileMetadataRepository metadataRepository;

    public FileStorageService(FileMetadataRepository metadataRepository) throws IOException {
        this.metadataRepository = metadataRepository;
        this.uploadPath = Paths.get(FileStorageConfig.UPLOAD_DIR);
        Files.createDirectories(uploadPath);
        System.out.println("File storage initialized at: " + uploadPath.toAbsolutePath());
    }

    /**
     * Store uploaded file with validation
     */
    public FileMetadata storeFile(MultipartFile file) {
        try {
            // Validation
            if (file.isEmpty()) {
                throw new FileStorageException("Cannot store empty file");
            }

            if (file.getSize() > FileStorageConfig.MAX_FILE_SIZE) {
                throw new FileStorageException("File size exceeds maximum limit of 10MB");
            }

            String extension = FilenameUtils.getExtension(file.getOriginalFilename());
            if (!FileStorageConfig.ALLOWED_EXTENSIONS.contains(extension.toLowerCase())) {
                throw new FileStorageException("File type not allowed: " + extension);
            }

            // Generate unique filename
            String storedFilename = UUID.randomUUID().toString() + "." + extension;
            Path targetLocation = uploadPath.resolve(storedFilename);

            // Save file to disk
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            // Save metadata to database
            FileMetadata metadata = new FileMetadata(
                storedFilename,
                file.getOriginalFilename(),
                file.getSize(),
                file.getContentType()
            );
            metadataRepository.save(metadata);

            System.out.println("File stored: " + storedFilename + " (Original: " + file.getOriginalFilename() + ")");
            return metadata;

        } catch (IOException e) {
            throw new FileStorageException("Failed to store file", e);
        }
    }

    /**
     * Load file content
     */
    public FileData loadFile(Long fileId) {
        FileMetadata metadata = metadataRepository.findById(fileId)
            .orElseThrow(() -> new FileStorageException("File not found with id: " + fileId));

        try {
            Path filePath = uploadPath.resolve(metadata.getStoredFilename());
            byte[] data = Files.readAllBytes(filePath);
            return new FileData(metadata, data);
        } catch (IOException e) {
            throw new FileStorageException("Failed to load file", e);
        }
    }

    /**
     * Delete file
     */
    public boolean deleteFile(Long fileId) {
        Optional<FileMetadata> metadataOpt = metadataRepository.findById(fileId);
        if (metadataOpt.isEmpty()) {
            return false;
        }

        FileMetadata metadata = metadataOpt.get();
        try {
            Path filePath = uploadPath.resolve(metadata.getStoredFilename());
            Files.deleteIfExists(filePath);
            metadataRepository.delete(metadata);
            System.out.println("File deleted: " + metadata.getStoredFilename());
            return true;
        } catch (IOException e) {
            throw new FileStorageException("Failed to delete file", e);
        }
    }

    /**
     * List all files
     */
    public List<FileMetadata> listAllFiles() {
        return metadataRepository.findAll();
    }

    /**
     * Get file statistics
     */
    public Map<String, Object> getStatistics() {
        List<FileMetadata> allFiles = metadataRepository.findAll();
        long totalSize = allFiles.stream().mapToLong(FileMetadata::getFileSize).sum();

        Map<String, Long> byType = allFiles.stream()
            .collect(Collectors.groupingBy(
                f -> f.getContentType() != null ? f.getContentType() : "unknown",
                Collectors.counting()
            ));

        return Map.of(
            "totalFiles", allFiles.size(),
            "totalSize", totalSize,
            "totalSizeMB", totalSize / (1024.0 * 1024.0),
            "filesByType", byType
        );
    }
}

// DTO: FileData
class FileData {
    private final FileMetadata metadata;
    private final byte[] data;

    public FileData(FileMetadata metadata, byte[] data) {
        this.metadata = metadata;
        this.data = data;
    }

    public FileMetadata getMetadata() { return metadata; }
    public byte[] getData() { return data; }
}

// Controller: FileUploadController
@RestController
@RequestMapping("/api/files")
class FileUploadController {
    private final FileStorageService storageService;

    public FileUploadController(FileStorageService storageService) {
        this.storageService = storageService;
    }

    /**
     * Upload file
     */
    @PostMapping("/upload")
    public ResponseEntity<Map<String, Object>> uploadFile(@RequestParam("file") MultipartFile file) {
        try {
            FileMetadata metadata = storageService.storeFile(file);

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "File uploaded successfully");
            response.put("fileId", metadata.getId());
            response.put("filename", metadata.getOriginalFilename());
            response.put("size", metadata.getFileSize());
            response.put("uploadedAt", metadata.getUploadedAt());

            return ResponseEntity.ok(response);
        } catch (FileStorageException e) {
            return ResponseEntity.badRequest()
                .body(Map.of("success", false, "error", e.getMessage()));
        }
    }

    /**
     * List all files
     */
    @GetMapping
    public ResponseEntity<List<Map<String, Object>>> listFiles() {
        List<FileMetadata> files = storageService.listAllFiles();

        List<Map<String, Object>> response = files.stream().map(f -> {
            Map<String, Object> fileInfo = new HashMap<>();
            fileInfo.put("id", f.getId());
            fileInfo.put("originalFilename", f.getOriginalFilename());
            fileInfo.put("size", f.getFileSize());
            fileInfo.put("contentType", f.getContentType());
            fileInfo.put("uploadedAt", f.getUploadedAt());
            return fileInfo;
        }).collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }

    /**
     * Download file
     */
    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> downloadFile(@PathVariable Long id) {
        try {
            FileData fileData = storageService.loadFile(id);
            FileMetadata metadata = fileData.getMetadata();

            ByteArrayResource resource = new ByteArrayResource(fileData.getData());

            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\"" + metadata.getOriginalFilename() + "\"")
                .contentType(MediaType.parseMediaType(
                    metadata.getContentType() != null ? metadata.getContentType() : MediaType.APPLICATION_OCTET_STREAM_VALUE
                ))
                .contentLength(metadata.getFileSize())
                .body(resource);
        } catch (FileStorageException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Get file metadata
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getFileMetadata(@PathVariable Long id) {
        try {
            FileData fileData = storageService.loadFile(id);
            FileMetadata metadata = fileData.getMetadata();

            Map<String, Object> response = new HashMap<>();
            response.put("id", metadata.getId());
            response.put("originalFilename", metadata.getOriginalFilename());
            response.put("size", metadata.getFileSize());
            response.put("contentType", metadata.getContentType());
            response.put("uploadedAt", metadata.getUploadedAt());

            return ResponseEntity.ok(response);
        } catch (FileStorageException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Delete file
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteFile(@PathVariable Long id) {
        boolean deleted = storageService.deleteFile(id);
        if (deleted) {
            return ResponseEntity.ok(Map.of("success", true, "message", "File deleted"));
        }
        return ResponseEntity.notFound().build();
    }

    /**
     * Get statistics
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStatistics() {
        return ResponseEntity.ok(storageService.getStatistics());
    }
}

// Global Exception Handler
@RestControllerAdvice
class FileUploadExceptionHandler {
    @ExceptionHandler(FileStorageException.class)
    public ResponseEntity<Map<String, String>> handleFileStorageException(FileStorageException e) {
        return ResponseEntity.badRequest()
            .body(Map.of("error", e.getMessage()));
    }

    @ExceptionHandler(org.springframework.web.multipart.MaxUploadSizeExceededException.class)
    public ResponseEntity<Map<String, String>> handleMaxSizeException(org.springframework.web.multipart.MaxUploadSizeExceededException e) {
        return ResponseEntity.badRequest()
            .body(Map.of("error", "File size exceeds maximum upload size"));
    }
}
