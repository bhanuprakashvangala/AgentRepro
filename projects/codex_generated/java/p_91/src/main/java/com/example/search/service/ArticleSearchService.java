package com.example.search.service;

import com.example.search.model.ArticleDocument;
import com.example.search.repository.ArticleRepository;
import java.time.Instant;
import java.util.List;
import org.elasticsearch.index.query.BoolQueryBuilder;
import org.elasticsearch.index.query.QueryBuilders;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.annotations.FieldType;
import org.springframework.data.elasticsearch.client.elc.NativeQueryBuilder;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.core.SearchPage;
import org.springframework.data.elasticsearch.core.SearchPageImpl;
import org.springframework.data.elasticsearch.core.query.NativeQuery;
import org.springframework.stereotype.Service;

@Service
public class ArticleSearchService {

    private final ArticleRepository repository;
    private final ElasticsearchOperations operations;

    public ArticleSearchService(ArticleRepository repository, ElasticsearchOperations operations) {
        this.repository = repository;
        this.operations = operations;
    }

    public ArticleDocument index(ArticleDocument document) {
        if (document.getPublishedAt() == null) {
            document.setPublishedAt(Instant.now());
        }
        return repository.save(document);
    }

    public Page<ArticleDocument> list(Pageable pageable) {
        return repository.findAll(pageable);
    }

    public SearchPage<ArticleDocument> search(String query, List<String> tags, String author, Pageable pageable) {
        BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();

        if (query != null && !query.isBlank()) {
            boolQuery.must(QueryBuilders.multiMatchQuery(query, "title", "body"));
        } else {
            boolQuery.must(QueryBuilders.matchAllQuery());
        }

        if (tags != null && !tags.isEmpty()) {
            boolQuery.filter(QueryBuilders.termsQuery("tags", tags));
        }

        if (author != null && !author.isBlank()) {
            boolQuery.filter(QueryBuilders.termQuery("author", author));
        }

        NativeQuery searchQuery = new NativeQueryBuilder()
                .withQuery(boolQuery)
                .withPageable(pageable)
                .build();

        SearchHits<ArticleDocument> hits = operations.search(searchQuery, ArticleDocument.class);
        return SearchPageImpl.of(hits, pageable);
    }
}
