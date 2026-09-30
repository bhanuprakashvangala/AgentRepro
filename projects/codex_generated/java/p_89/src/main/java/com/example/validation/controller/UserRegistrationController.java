package com.example.validation.controller;

import com.example.validation.model.UserRegistrationRequest;
import com.example.validation.service.UserRegistrationService;
import jakarta.validation.Valid;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/users")
public class UserRegistrationController {

    private final UserRegistrationService registrationService;

    public UserRegistrationController(UserRegistrationService registrationService) {
        this.registrationService = registrationService;
    }

    @PostMapping
    public ResponseEntity<Map<String, Object>> register(@RequestBody @Valid UserRegistrationRequest request) {
        String userId = registrationService.register(request);
        return ResponseEntity.ok(Map.of(
                "status", "created",
                "userId", userId
        ));
    }
}
