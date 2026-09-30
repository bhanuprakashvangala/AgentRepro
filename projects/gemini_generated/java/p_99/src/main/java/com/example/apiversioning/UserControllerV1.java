package com.example.apiversioning;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/v1/users")
public class UserControllerV1 {

    @GetMapping
    public ResponseEntity<String> getUser() {
        return ResponseEntity.ok("User API V1");
    }
}
