package com.example.searchservice;

import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

import java.util.List;

public interface ProductRepository extends ElasticsearchRepository<Product, String> {

    List<Product> findByNameContainingOrDescriptionContaining(String name, String description);

    List<Product> findByPriceBetween(double minPrice, double maxPrice);
}
