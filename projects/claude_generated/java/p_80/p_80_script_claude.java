package com.example.httpclient;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.hc.client5.http.classic.methods.*;
import org.apache.hc.client5.http.config.RequestConfig;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.impl.io.PoolingHttpClientConnectionManager;
import org.apache.hc.core5.http.ContentType;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.apache.hc.core5.http.io.entity.StringEntity;
import org.apache.hc.core5.util.Timeout;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class HttpClientService {
    private static final Logger logger = LoggerFactory.getLogger(HttpClientService.class);
    private final CloseableHttpClient httpClient;
    private final ObjectMapper objectMapper;
    private final int maxRetries;
    private final long retryDelayMs;

    public HttpClientService() {
        this(3, 1000);
    }

    public HttpClientService(int maxRetries, long retryDelayMs) {
        this.maxRetries = maxRetries;
        this.retryDelayMs = retryDelayMs;
        this.objectMapper = new ObjectMapper();

        // Configure connection pool
        PoolingHttpClientConnectionManager connectionManager = new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(100);
        connectionManager.setDefaultMaxPerRoute(20);

        // Configure request timeouts
        RequestConfig requestConfig = RequestConfig.custom()
                .setConnectTimeout(Timeout.of(10, TimeUnit.SECONDS))
                .setResponseTimeout(Timeout.of(30, TimeUnit.SECONDS))
                .build();

        this.httpClient = HttpClients.custom()
                .setConnectionManager(connectionManager)
                .setDefaultRequestConfig(requestConfig)
                .build();

        logger.info("HttpClientService initialized with maxRetries={}, retryDelayMs={}", maxRetries, retryDelayMs);
    }

    /**
     * Execute GET request
     */
    public HttpResponse get(String url, Map<String, String> headers) throws IOException {
        return executeWithRetry(() -> {
            HttpGet request = new HttpGet(url);
            setHeaders(request, headers);
            return execute(request);
        });
    }

    /**
     * Execute POST request with JSON body
     */
    public HttpResponse post(String url, Object body, Map<String, String> headers) throws IOException {
        return executeWithRetry(() -> {
            HttpPost request = new HttpPost(url);
            setHeaders(request, headers);
            if (body != null) {
                String jsonBody = objectMapper.writeValueAsString(body);
                request.setEntity(new StringEntity(jsonBody, ContentType.APPLICATION_JSON));
            }
            return execute(request);
        });
    }

    /**
     * Execute PUT request with JSON body
     */
    public HttpResponse put(String url, Object body, Map<String, String> headers) throws IOException {
        return executeWithRetry(() -> {
            HttpPut request = new HttpPut(url);
            setHeaders(request, headers);
            if (body != null) {
                String jsonBody = objectMapper.writeValueAsString(body);
                request.setEntity(new StringEntity(jsonBody, ContentType.APPLICATION_JSON));
            }
            return execute(request);
        });
    }

    /**
     * Execute DELETE request
     */
    public HttpResponse delete(String url, Map<String, String> headers) throws IOException {
        return executeWithRetry(() -> {
            HttpDelete request = new HttpDelete(url);
            setHeaders(request, headers);
            return execute(request);
        });
    }

    /**
     * Execute request with retry logic
     */
    private HttpResponse executeWithRetry(HttpCallable callable) throws IOException {
        int attempt = 0;
        IOException lastException = null;

        while (attempt < maxRetries) {
            try {
                return callable.call();
            } catch (IOException e) {
                lastException = e;
                attempt++;
                if (attempt < maxRetries) {
                    long delay = retryDelayMs * (long) Math.pow(2, attempt - 1); // Exponential backoff
                    logger.warn("Request failed (attempt {}/{}). Retrying in {}ms...", attempt, maxRetries, delay);
                    try {
                        Thread.sleep(delay);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new IOException("Retry interrupted", ie);
                    }
                }
            }
        }

        logger.error("Request failed after {} attempts", maxRetries);
        throw lastException;
    }

    /**
     * Execute HTTP request
     */
    private HttpResponse execute(ClassicHttpRequest request) throws IOException {
        logger.info("Executing {} {}", request.getMethod(), request.getRequestUri());

        return httpClient.execute(request, response -> {
            int statusCode = response.getCode();
            String body = EntityUtils.toString(response.getEntity());

            logger.info("Response: status={}, bodyLength={}", statusCode, body.length());

            return new HttpResponse(statusCode, body);
        });
    }

    /**
     * Set headers on request
     */
    private void setHeaders(ClassicHttpRequest request, Map<String, String> headers) {
        if (headers != null) {
            headers.forEach(request::setHeader);
        }
    }

    /**
     * Parse JSON response
     */
    public <T> T parseJson(String json, Class<T> clazz) throws IOException {
        return objectMapper.readValue(json, clazz);
    }

    /**
     * Close HTTP client
     */
    public void close() throws IOException {
        if (httpClient != null) {
            httpClient.close();
            logger.info("HttpClient closed");
        }
    }

    @FunctionalInterface
    private interface HttpCallable {
        HttpResponse call() throws IOException;
    }

    // Example usage
    public static void main(String[] args) {
        HttpClientService client = new HttpClientService(3, 1000);

        try {
            // Test 1: GET request
            System.out.println("\n=== Test 1: GET Request ===");
            HttpResponse response1 = client.get("https://jsonplaceholder.typicode.com/posts/1", null);
            System.out.println("Status: " + response1.getStatusCode());
            System.out.println("Body: " + response1.getBody().substring(0, Math.min(100, response1.getBody().length())));

            // Test 2: POST request
            System.out.println("\n=== Test 2: POST Request ===");
            Map<String, Object> postData = new HashMap<>();
            postData.put("title", "Test Post");
            postData.put("body", "This is a test post");
            postData.put("userId", 1);

            HttpResponse response2 = client.post("https://jsonplaceholder.typicode.com/posts", postData, null);
            System.out.println("Status: " + response2.getStatusCode());
            System.out.println("Body: " + response2.getBody());

            // Test 3: PUT request
            System.out.println("\n=== Test 3: PUT Request ===");
            Map<String, Object> putData = new HashMap<>();
            putData.put("id", 1);
            putData.put("title", "Updated Title");
            putData.put("body", "Updated body");
            putData.put("userId", 1);

            HttpResponse response3 = client.put("https://jsonplaceholder.typicode.com/posts/1", putData, null);
            System.out.println("Status: " + response3.getStatusCode());

            // Test 4: DELETE request
            System.out.println("\n=== Test 4: DELETE Request ===");
            HttpResponse response4 = client.delete("https://jsonplaceholder.typicode.com/posts/1", null);
            System.out.println("Status: " + response4.getStatusCode());

            // Test 5: Parse JSON response
            System.out.println("\n=== Test 5: Parse JSON ===");
            HttpResponse response5 = client.get("https://jsonplaceholder.typicode.com/users/1", null);
            Map<String, Object> user = client.parseJson(response5.getBody(), Map.class);
            System.out.println("User name: " + user.get("name"));
            System.out.println("User email: " + user.get("email"));

            // Test 6: With custom headers
            System.out.println("\n=== Test 6: Custom Headers ===");
            Map<String, String> headers = new HashMap<>();
            headers.put("User-Agent", "HttpClientService/1.0");
            headers.put("Accept", "application/json");

            HttpResponse response6 = client.get("https://jsonplaceholder.typicode.com/posts", headers);
            System.out.println("Status: " + response6.getStatusCode());
            System.out.println("Posts count: " + response6.getBody().split("\\{").length);

        } catch (IOException e) {
            logger.error("Request failed", e);
        } finally {
            try {
                client.close();
            } catch (IOException e) {
                logger.error("Failed to close client", e);
            }
        }
    }
}

/**
 * HTTP Response wrapper
 */
class HttpResponse {
    private final int statusCode;
    private final String body;

    public HttpResponse(int statusCode, String body) {
        this.statusCode = statusCode;
        this.body = body;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getBody() {
        return body;
    }

    public boolean isSuccess() {
        return statusCode >= 200 && statusCode < 300;
    }

    @Override
    public String toString() {
        return "HttpResponse{statusCode=" + statusCode + ", bodyLength=" + body.length() + "}";
    }
}
