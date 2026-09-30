package com.example.fileupload;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.util.Arrays;
import java.util.List;

@RestController
public class FileUploadController {

    private final FileStorageService fileStorageService;

    @Autowired
    public FileUploadController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<String> uploadFile(@RequestParam("file") MultipartFile file) {
        // Validate file type
        List<String> allowedFileTypes = Arrays.asList("image/png", "image/jpeg");
        if (!allowedFileTypes.contains(file.getContentType())) {
            return ResponseEntity.badRequest().body("Invalid file type. Only PNG and JPG are allowed.");
        }

        String fileName = fileStorageService.storeFile(file);

        return ResponseEntity.ok("File uploaded successfully: " + fileName);
    }
}
