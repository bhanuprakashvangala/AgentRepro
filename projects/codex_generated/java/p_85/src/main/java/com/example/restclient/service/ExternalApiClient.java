package com.example.restclient.service;

import com.example.restclient.exception.ApiClientException;
import com.example.restclient.web.dto.PostRequest;
import com.example.restclient.web.dto.PostResponse;
import java.net.URI;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Service
public class ExternalApiClient {

    private static final Logger logger = LoggerFactory.getLogger(ExternalApiClient.class);
    private final String baseUrl;

    private final RestTemplate restTemplate;

    public ExternalApiClient(RestTemplate restTemplate, @Value("${client.base-url}") String baseUrl) {
        this.restTemplate = restTemplate;
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
    }

    @Retryable(
            include = {HttpStatusCodeException.class, ResourceAccessException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public List<PostResponse> fetchPosts() {
        try {
            String url = postsEndpoint();
            ResponseEntity<PostResponse[]> response = restTemplate.getForEntity(url, PostResponse[].class);
            PostResponse[] body = response.getBody();
            return body != null ? List.of(body) : List.of();
        } catch (HttpStatusCodeException ex) {
            handleError("GET", postsEndpoint(), ex);
            throw wrap(ex, "Failed to fetch posts");
        } catch (ResourceAccessException ex) {
            logger.error("GET {} failed: {}", postsEndpoint(), ex.getMessage());
            throw new ApiClientException("Remote service unreachable", HttpStatusCode.valueOf(503), null, ex);
        }
    }

    @Retryable(
            include = {HttpStatusCodeException.class, ResourceAccessException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public PostResponse createPost(PostRequest request) {
        try {
            String url = postsEndpoint();
            ResponseEntity<PostResponse> response = restTemplate.postForEntity(url, request, PostResponse.class);
            return response.getBody();
        } catch (HttpStatusCodeException ex) {
            handleError("POST", postsEndpoint(), ex);
            throw wrap(ex, "Failed to create post");
        } catch (ResourceAccessException ex) {
            logger.error("POST {} failed: {}", postsEndpoint(), ex.getMessage());
            throw new ApiClientException("Remote service unreachable", HttpStatusCode.valueOf(503), null, ex);
        }
    }

    @Retryable(
            include = {HttpStatusCodeException.class, ResourceAccessException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public PostResponse updatePost(long id, PostRequest request) {
        URI uri = postByIdEndpoint(id);
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<PostRequest> entity = new HttpEntity<>(request, headers);
            ResponseEntity<PostResponse> response = restTemplate.exchange(uri, HttpMethod.PUT, entity, PostResponse.class);
            return response.getBody();
        } catch (HttpStatusCodeException ex) {
            handleError("PUT", uri.toString(), ex);
            throw wrap(ex, "Failed to update post");
        } catch (ResourceAccessException ex) {
            logger.error("PUT {} failed: {}", uri, ex.getMessage());
            throw new ApiClientException("Remote service unreachable", HttpStatusCode.valueOf(503), null, ex);
        }
    }

    @Retryable(
            include = {HttpStatusCodeException.class, ResourceAccessException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public void deletePost(long id) {
        URI uri = postByIdEndpoint(id);
        try {
            restTemplate.delete(uri);
        } catch (HttpStatusCodeException ex) {
            handleError("DELETE", uri.toString(), ex);
            throw wrap(ex, "Failed to delete post");
        } catch (ResourceAccessException ex) {
            logger.error("DELETE {} failed: {}", uri, ex.getMessage());
            throw new ApiClientException("Remote service unreachable", HttpStatusCode.valueOf(503), null, ex);
        }
    }

    private void handleError(String method, String url, HttpStatusCodeException ex) {
        logger.error("{} {} failed with status {} and body {}", method, url, ex.getStatusCode(), ex.getResponseBodyAsString());
    }

    private ApiClientException wrap(HttpStatusCodeException ex, String message) {
        return new ApiClientException(message, ex.getStatusCode(), ex.getResponseBodyAsString(), ex);
    }

    private String postsEndpoint() {
        return baseUrl + "/posts";
    }

    private URI postByIdEndpoint(long id) {
        return UriComponentsBuilder.fromHttpUrl(postsEndpoint())
                .pathSegment(String.valueOf(id))
                .build()
                .toUri();
    }
}
