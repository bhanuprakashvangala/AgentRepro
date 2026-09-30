package com.example.restclient.web;

import com.example.restclient.service.ExternalApiClient;
import com.example.restclient.web.dto.PostRequest;
import com.example.restclient.web.dto.PostResponse;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/posts")
public class ClientController {

    private final ExternalApiClient client;

    public ClientController(ExternalApiClient client) {
        this.client = client;
    }

    @GetMapping
    public List<PostResponse> list() {
        return client.fetchPosts();
    }

    @PostMapping
    public ResponseEntity<PostResponse> create(@RequestBody @Valid PostRequest request) {
        return ResponseEntity.ok(client.createPost(request));
    }

    @PutMapping("/{id}")
    public ResponseEntity<PostResponse> update(@PathVariable long id, @RequestBody @Valid PostRequest request) {
        return ResponseEntity.ok(client.updatePost(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> delete(@PathVariable long id) {
        client.deletePost(id);
        return ResponseEntity.ok(Map.of("id", id, "status", "deleted"));
    }
}
