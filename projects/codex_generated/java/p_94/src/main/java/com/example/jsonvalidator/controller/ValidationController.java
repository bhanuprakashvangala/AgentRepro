package com.example.jsonvalidator.controller;

import com.example.jsonvalidator.model.ValidationRequest;
import com.example.jsonvalidator.model.ValidationResponse;
import com.example.jsonvalidator.service.JsonValidationService;
import com.fasterxml.jackson.core.JsonProcessingException;
import java.io.IOException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/json")
public class ValidationController {

    private static final Logger logger = LoggerFactory.getLogger(ValidationController.class);

    private final JsonValidationService validationService;

    public ValidationController(JsonValidationService validationService) {
        this.validationService = validationService;
    }

    @PostMapping("/validate")
    public ResponseEntity<ValidationResponse> validate(@RequestBody @Validated ValidationRequest request)
            throws IOException {
        Object parsed = validationService.parse(request.getJson());
        List<String> errors = validationService.validate(request.getSchemaName(), request.getJson());
        boolean valid = errors.isEmpty();
        ValidationResponse response = new ValidationResponse(valid, errors, parsed);
        return ResponseEntity.ok(response);
    }

    @ExceptionHandler(JsonProcessingException.class)
    public ResponseEntity<ValidationResponse> handleParsingError(JsonProcessingException ex) {
        logger.error("JSON parse error", ex);
        ValidationResponse response = new ValidationResponse(false, List.of("Invalid JSON: " + ex.getOriginalMessage()), null);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    @ExceptionHandler(IOException.class)
    public ResponseEntity<ValidationResponse> handleSchemaError(IOException ex) {
        logger.error("Schema load error", ex);
        ValidationResponse response = new ValidationResponse(false, List.of(ex.getMessage()), null);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }
}
