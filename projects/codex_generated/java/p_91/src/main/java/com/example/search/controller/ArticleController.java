package com.example.search.controller;

import com.example.search.model.ArticleDocument;
import com.example.search.service.ArticleSearchService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import java.util.List;
import java.util.Map;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.elasticsearch.core.SearchPage;
import org.springframework.data.elasticsearch.core.SearchPageImpl;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/articles")
@Validated
public class ArticleController {

    private final ArticleSearchService articleSearchService;

    public ArticleController(ArticleSearchService articleSearchService) {
        this.articleSearchService = articleSearchService;
    }

    @PostMapping
    public ResponseEntity<ArticleDocument> index(@RequestBody @Valid ArticleDocument document) {
        ArticleDocument saved = articleSearchService.index(document);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> search(
            @RequestParam(value = "q", required = false) String query,
            @RequestParam(value = "tags", required = false) List<String> tags,
            @RequestParam(value = "author", required = false) String author,
            @RequestParam(value = "page", defaultValue = "0") int page,
            @RequestParam(value = "size", defaultValue = "10") int size,
            @RequestParam(value = "sort", defaultValue = "publishedAt") String sort,
            @RequestParam(value = "direction", defaultValue = "DESC") Sort.Direction direction
    ) {
        Pageable pageable = PageRequest.of(page, size, direction, sort);
        SearchPage<ArticleDocument> results = articleSearchService.search(query, tags, author, pageable);
        return ResponseEntity.ok(Map.of(
                "totalHits", results.getTotalElements(),
                "totalPages", results.getTotalPages(),
                "page", page,
                "size", size,
                "content", results.getContent()
        ));
    }
}
