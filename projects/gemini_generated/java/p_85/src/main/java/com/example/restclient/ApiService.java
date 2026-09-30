package com.example.restclient;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.List;
import java.util.Objects;

@Service
public class ApiService {

    private static final String BASE_URL = "https://jsonplaceholder.typicode.com/posts";

    private final RestTemplate restTemplate;

    @Autowired
    public ApiService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Retryable(value = {ResourceAccessException.class, HttpServerErrorException.class},
               maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
    public List<Post> getAllPosts() {
        ResponseEntity<Post[]> response = restTemplate.getForEntity(BASE_URL, Post[].class);
        return Arrays.asList(Objects.requireNonNull(response.getBody()));
    }

    @Retryable(value = {ResourceAccessException.class, HttpServerErrorException.class},
               maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
    public Post getPostById(Long id) {
        try {
            return restTemplate.getForObject(BASE_URL + "/" + id, Post.class);
        } catch (HttpClientErrorException e) {
            if (e.getStatusCode().is4xxClientError()) {
                System.err.println("Client error: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
            }
            throw e;
        }
    }

    @Retryable(value = {ResourceAccessException.class, HttpServerErrorException.class},
               maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
    public Post createPost(Post post) {
        return restTemplate.postForObject(BASE_URL, post, Post.class);
    }

    @Retryable(value = {ResourceAccessException.class, HttpServerErrorException.class},
               maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
    public void updatePost(Long id, Post post) {
        restTemplate.put(BASE_URL + "/" + id, post);
    }

    @Retryable(value = {ResourceAccessException.class, HttpServerErrorException.class},
               maxAttempts = 3, backoff = @Backoff(delay = 1000, multiplier = 2))
    public void deletePost(Long id) {
        restTemplate.delete(BASE_URL + "/" + id);
    }
}
