package com.example.passwordencryption;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PasswordController {

    private final PasswordService passwordService;

    @Autowired
    public PasswordController(PasswordService passwordService) {
        this.passwordService = passwordService;
    }

    @PostMapping("/hash")
    public ResponseEntity<String> hashPassword(@RequestParam String password) {
        String hashedPassword = passwordService.hashPassword(password);
        return ResponseEntity.ok(hashedPassword);
    }

    @PostMapping("/verify")
    public ResponseEntity<String> verifyPassword(@RequestParam String rawPassword, @RequestParam String encodedPassword) {
        boolean isMatch = passwordService.verifyPassword(rawPassword, encodedPassword);
        if (isMatch) {
            return ResponseEntity.ok("Password matches!");
        } else {
            return ResponseEntity.ok("Password does not match.");
        }
    }
}
