package com.example.versioning.controller;

import com.example.versioning.config.ApiVersionHeaderResolver;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/users")
@Tag(name = "Users (header versioned)", description = "API versioning via X-API-Version header")
public class HeaderVersionedController {

    @GetMapping
    @Operation(summary = "List users with header versioning", description = "Set X-API-Version header to choose response format")
    public ResponseEntity<?> listUsers(HttpServletRequest request) {
        String version = ApiVersionHeaderResolver.resolve(request);
        if (version == null || version.equals("1")) {
            request.setAttribute("deprecation-warning", "API version 1 is deprecated; use version 2.");
            return ResponseEntity.ok(Map.of(
                    "version", "1",
                    "users", new String[]{"legacy-user-1", "legacy-user-2"}
            ));
        } else if (version.equals("2")) {
            return ResponseEntity.ok(Map.of(
                    "version", "2",
                    "users", new String[]{"modern-user-1", "modern-user-2"},
                    "count", 2
            ));
        }
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of(
                "error", "Unsupported API version",
                "supported", new int[]{1, 2}
        ));
    }
}
