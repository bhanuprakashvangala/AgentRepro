package com.example.apiversioning;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/products")
public class ProductController {

    @GetMapping(produces = "application/vnd.api.v1+json")
    public ResponseEntity<String> getProductV1() {
        return ResponseEntity.ok("Product API V1 (Header)");
    }

    @GetMapping(produces = "application/vnd.api.v2+json")
    public ResponseEntity<String> getProductV2() {
        return ResponseEntity.ok("Product API V2 (Header)");
    }
}
