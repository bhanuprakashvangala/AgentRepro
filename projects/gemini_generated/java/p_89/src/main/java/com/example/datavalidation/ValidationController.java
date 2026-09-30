package com.example.datavalidation;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;

@RestController
public class ValidationController {

    @PostMapping("/users")
    public ResponseEntity<String> createUser(@Valid @RequestBody UserDto userDto) {
        // If validation passes, do something with the userDto
        return ResponseEntity.ok("User created successfully");
    }
}
