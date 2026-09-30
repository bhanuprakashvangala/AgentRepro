package com.example.csvimporter.controller;

import com.example.csvimporter.service.CsvImportService;
import jakarta.validation.constraints.NotBlank;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@Validated
public class ImportController {

    private final CsvImportService importService;

    public ImportController(CsvImportService importService) {
        this.importService = importService;
    }

    @PostMapping("/api/import")
    public ResponseEntity<String> importCsv(@RequestParam("path") @NotBlank String path) throws IOException {
        Path csvPath = Paths.get(path);
        if (!Files.exists(csvPath) || !Files.isRegularFile(csvPath)) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("File does not exist: " + path);
        }
        int imported = importService.importCsv(csvPath);
        return ResponseEntity.ok("Imported " + imported + " records from " + path);
    }
}
