package com.example.versioning.controller;

import com.example.versioning.config.ApiVersionHeaderResolver;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.Map;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/users")
@Tag(name = "Users v1", description = "Legacy user API")
public class UserControllerV1 {

    @GetMapping
    @Operation(summary = "List users", description = "Version 1 returning minimal user information")
    public ResponseEntity<List<Map<String, Object>>> listUsers(HttpServletRequest request) {
        warnDeprecated(request);
        return ResponseEntity.ok(List.of(
                Map.of("id", 1, "name", "Alice v1"),
                Map.of("id", 2, "name", "Bob v1")
        ));
    }

    private void warnDeprecated(HttpServletRequest request) {
        request.setAttribute("deprecation-warning", "API version v1 is deprecated and will be removed soon.");
    }
}
