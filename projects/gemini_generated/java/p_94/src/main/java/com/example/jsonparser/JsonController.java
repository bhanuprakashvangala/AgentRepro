package com.example.jsonparser;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.networknt.schema.ValidationMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;
import java.util.Set;

@RestController
@RequestMapping("/json")
public class JsonController {

    private final JsonValidationService jsonValidationService;

    @Autowired
    public JsonController(JsonValidationService jsonValidationService) {
        this.jsonValidationService = jsonValidationService;
    }

    @PostMapping("/parse")
    public ResponseEntity<?> parseJson(@RequestBody String jsonString) {
        try {
            User user = jsonValidationService.parseJson(jsonString, User.class);
            return ResponseEntity.ok(user);
        } catch (JsonProcessingException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error parsing JSON: " + e.getMessage());
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Internal server error: " + e.getMessage());
        }
    }

    @PostMapping("/validate")
    public ResponseEntity<?> validateJson(@RequestBody String jsonString) {
        try {
            Set<ValidationMessage> errors = jsonValidationService.validateJson(jsonString);
            if (errors.isEmpty()) {
                return ResponseEntity.ok("JSON is valid.");
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(errors);
            }
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Error reading JSON: " + e.getMessage());
        }
    }
}
