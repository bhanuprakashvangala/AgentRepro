package com.example.versioning.controller;

import com.example.versioning.config.ApiVersionHeaderResolver;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v2/users")
@Tag(name = "Users v2", description = "Current user API")
public class UserControllerV2 {

    @GetMapping
    @Operation(summary = "List users", description = "Version 2 returning extended user information")
    public ResponseEntity<List<Map<String, Object>>> listUsers() {
        return ResponseEntity.ok(List.of(
                Map.of("id", 1, "name", "Alice v2", "email", "alice@example.com"),
                Map.of("id", 2, "name", "Bob v2", "email", "bob@example.com")
        ));
    }
}
