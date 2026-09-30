package com.example.connectionpool;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class DatabaseController {

    private final DatabaseService databaseService;

    @Autowired
    public DatabaseController(DatabaseService databaseService) {
        this.databaseService = databaseService;
    }

    @GetMapping("/users")
    public ResponseEntity<List<Map<String, Object>>> getAllUsers() {
        return ResponseEntity.ok(databaseService.getAllUsers());
    }

    @PostMapping("/users")
    public ResponseEntity<String> addUser(@RequestParam String name) {
        databaseService.addUser(name);
        return ResponseEntity.ok("User added successfully!");
    }

    @GetMapping("/h2-console")
    public String h2Console() {
        return "H2 console is available at /h2-console. Please ensure you have enabled it in application.properties.";
    }
}
