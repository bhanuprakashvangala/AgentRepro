package com.example.searchservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/products")
public class ProductController {

    private final ProductService productService;

    @Autowired
    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @PostMapping
    public ResponseEntity<Product> createProduct(@RequestBody Product product) {
        return ResponseEntity.ok(productService.save(product));
    }

    @GetMapping("/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable String id) {
        return ResponseEntity.ok(productService.findById(id));
    }

    @GetMapping("/search")
    public ResponseEntity<List<Product>> searchProducts(@RequestParam String query) {
        return ResponseEntity.ok(productService.search(query));
    }

    @GetMapping("/filter-by-price")
    public ResponseEntity<List<Product>> filterProductsByPrice(
            @RequestParam double minPrice,
            @RequestParam double maxPrice
    ) {
        return ResponseEntity.ok(productService.filterByPrice(minPrice, maxPrice));
    }

    @GetMapping("/search-and-paginate")
    public ResponseEntity<Page<Product>> searchAndPaginateProducts(
            @RequestParam String query,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        return ResponseEntity.ok(productService.searchAndPaginate(query, page, size));
    }

    @PostMapping("/index-sample-data")
    public ResponseEntity<String> indexSampleData() {
        productService.indexSampleData();
        return ResponseEntity.ok("Sample data indexed successfully!");
    }
}
