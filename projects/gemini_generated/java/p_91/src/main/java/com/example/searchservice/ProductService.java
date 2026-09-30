package com.example.searchservice;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.elasticsearch.core.ElasticsearchOperations;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.core.query.Criteria;
import org.springframework.data.elasticsearch.core.query.CriteriaQuery;
import org.springframework.data.elasticsearch.core.query.Query;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final ElasticsearchOperations elasticsearchOperations;

    @Autowired
    public ProductService(ProductRepository productRepository, ElasticsearchOperations elasticsearchOperations) {
        this.productRepository = productRepository;
        this.elasticsearchOperations = elasticsearchOperations;
    }

    public Product save(Product product) {
        return productRepository.save(product);
    }

    public Iterable<Product> saveAll(List<Product> products) {
        return productRepository.saveAll(products);
    }

    public Product findById(String id) {
        return productRepository.findById(id).orElse(null);
    }

    public Iterable<Product> findAll() {
        return productRepository.findAll();
    }

    public List<Product> search(String query) {
        Criteria criteria = new Criteria("name").contains(query)
                .or(new Criteria("description").contains(query));
        Query searchQuery = new CriteriaQuery(criteria);
        SearchHits<Product> searchHits = elasticsearchOperations.search(searchQuery, Product.class);
        return searchHits.stream().map(SearchHit::getContent).collect(Collectors.toList());
    }

    public List<Product> filterByPrice(double minPrice, double maxPrice) {
        return productRepository.findByPriceBetween(minPrice, maxPrice);
    }

    public Page<Product> searchAndPaginate(String query, int page, int size) {
        Criteria criteria = new Criteria("name").contains(query)
                .or(new Criteria("description").contains(query));
        Query searchQuery = new CriteriaQuery(criteria).setPageable(PageRequest.of(page, size));
        SearchHits<Product> searchHits = elasticsearchOperations.search(searchQuery, Product.class);
        return org.springframework.data.elasticsearch.core.SearchHitSupport.searchPageFor(searchHits, searchQuery.getPageable());
    }

    public void indexSampleData() {
        productRepository.deleteAll(); // Clear existing data
        save(new Product("1", "Laptop", "Powerful laptop for work and gaming", 1200.00));
        save(new Product("2", "Mouse", "Wireless mouse with ergonomic design", 25.00));
        save(new Product("3", "Keyboard", "Mechanical keyboard with RGB lighting", 75.00));
        save(new Product("4", "Monitor", "4K UHD monitor for stunning visuals", 350.00));
        save(new Product("5", "Webcam", "Full HD webcam for video calls", 50.00));
        save(new Product("6", "Headphones", "Noise-cancelling headphones with great sound", 150.00));
        save(new Product("7", "Microphone", "USB microphone for streaming and podcasting", 80.00));
        save(new Product("8", "Desk", "Adjustable standing desk", 400.00));
        save(new Product("9", "Chair", "Ergonomic office chair", 200.00));
        save(new Product("10", "SSD", "1TB NVMe SSD for fast storage", 100.00));
    }
}