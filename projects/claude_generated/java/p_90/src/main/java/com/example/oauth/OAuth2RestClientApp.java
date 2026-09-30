package com.example.oauth;

import com.google.gson.*;
import org.apache.hc.client5.http.classic.methods.*;
import org.apache.hc.client5.http.impl.classic.*;
import org.apache.hc.core5.http.*;
import org.apache.hc.core5.http.io.entity.*;
import org.apache.hc.client5.http.entity.UrlEncodedFormEntity;
import org.apache.hc.core5.http.message.BasicNameValuePair;
import org.apache.hc.core5.http.NameValuePair;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;

class OAuth2Config {
    private String tokenUrl;
    private String clientId;
    private String clientSecret;
    private String grantType;
    private String scope;
    private String username;
    private String password;

    public OAuth2Config(String tokenUrl, String clientId, String clientSecret, String grantType) {
        this.tokenUrl = tokenUrl;
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.grantType = grantType;
    }

    public String getTokenUrl() { return tokenUrl; }
    public String getClientId() { return clientId; }
    public String getClientSecret() { return clientSecret; }
    public String getGrantType() { return grantType; }
    public String getScope() { return scope; }
    public void setScope(String scope) { this.scope = scope; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}

class AccessToken {
    private String token;
    private String tokenType;
    private long expiresIn;
    private Instant issuedAt;
    private String scope;

    public AccessToken(String token, String tokenType, long expiresIn) {
        this.token = token;
        this.tokenType = tokenType;
        this.expiresIn = expiresIn;
        this.issuedAt = Instant.now();
    }

    public String getToken() { return token; }
    public String getTokenType() { return tokenType; }
    public long getExpiresIn() { return expiresIn; }
    public String getScope() { return scope; }
    public void setScope(String scope) { this.scope = scope; }

    public boolean isExpired() {
        // Consider token expired if within 60 seconds of expiration
        long expirationBuffer = 60;
        long secondsSinceIssued = Instant.now().getEpochSecond() - issuedAt.getEpochSecond();
        return secondsSinceIssued >= (expiresIn - expirationBuffer);
    }

    public String getAuthorizationHeader() {
        return tokenType + " " + token;
    }

    @Override
    public String toString() {
        return String.format("AccessToken{type=%s, expiresIn=%d, expired=%b}",
            tokenType, expiresIn, isExpired());
    }
}

class TokenManager {
    private final OAuth2Config config;
    private final CloseableHttpClient httpClient;
    private final Gson gson;
    private AccessToken currentToken;

    public TokenManager(OAuth2Config config) {
        this.config = config;
        this.httpClient = HttpClients.createDefault();
        this.gson = new Gson();
    }

    public synchronized AccessToken getAccessToken() throws IOException, org.apache.hc.core5.http.ParseException {
        if (currentToken == null || currentToken.isExpired()) {
            currentToken = requestNewToken();
        }
        return currentToken;
    }

    private AccessToken requestNewToken() throws IOException {
        System.out.println("Requesting new access token...");

        HttpPost httpPost = new HttpPost(config.getTokenUrl());

        // Build form data based on grant type
        List<NameValuePair> params = new ArrayList<>();
        params.add(new BasicNameValuePair("grant_type", config.getGrantType()));
        params.add(new BasicNameValuePair("client_id", config.getClientId()));
        params.add(new BasicNameValuePair("client_secret", config.getClientSecret()));

        if ("password".equals(config.getGrantType())) {
            params.add(new BasicNameValuePair("username", config.getUsername()));
            params.add(new BasicNameValuePair("password", config.getPassword()));
        }

        if (config.getScope() != null) {
            params.add(new BasicNameValuePair("scope", config.getScope()));
        }

        httpPost.setEntity(new UrlEncodedFormEntity(params, StandardCharsets.UTF_8));
        httpPost.setHeader("Content-Type", "application/x-www-form-urlencoded");

        try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
            int statusCode = response.getCode();

            if (statusCode != 200) {
                throw new IOException("Token request failed with status: " + statusCode);
            }

            String responseBody = EntityUtils.toString(response.getEntity());
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);

            String accessToken = jsonResponse.get("access_token").getAsString();
            String tokenType = jsonResponse.has("token_type")
                ? jsonResponse.get("token_type").getAsString()
                : "Bearer";
            long expiresIn = jsonResponse.has("expires_in")
                ? jsonResponse.get("expires_in").getAsLong()
                : 3600;

            AccessToken token = new AccessToken(accessToken, tokenType, expiresIn);

            if (jsonResponse.has("scope")) {
                token.setScope(jsonResponse.get("scope").getAsString());
            }

            System.out.println("Access token obtained successfully: " + token);
            return token;
        }
    }

    public void invalidateToken() {
        currentToken = null;
    }

    public void close() throws IOException {
        httpClient.close();
    }
}

class OAuth2RestClient {
    private final TokenManager tokenManager;
    private final CloseableHttpClient httpClient;
    private final Gson gson;
    private final String baseUrl;

    public OAuth2RestClient(String baseUrl, OAuth2Config config) {
        this.baseUrl = baseUrl;
        this.tokenManager = new TokenManager(config);
        this.httpClient = HttpClients.createDefault();
        this.gson = new GsonBuilder().setPrettyPrinting().create();
    }

    public String get(String path) throws IOException {
        return get(path, new HashMap<>());
    }

    public String get(String path, Map<String, String> headers) throws IOException {
        String url = buildUrl(path);
        HttpGet httpGet = new HttpGet(url);

        // Add OAuth token
        AccessToken token = tokenManager.getAccessToken();
        httpGet.setHeader("Authorization", token.getAuthorizationHeader());

        // Add custom headers
        headers.forEach(httpGet::setHeader);

        return executeRequest(httpGet);
    }

    public String post(String path, Object body) throws IOException {
        return post(path, body, new HashMap<>());
    }

    public String post(String path, Object body, Map<String, String> headers) throws IOException {
        String url = buildUrl(path);
        HttpPost httpPost = new HttpPost(url);

        // Add OAuth token
        AccessToken token = tokenManager.getAccessToken();
        httpPost.setHeader("Authorization", token.getAuthorizationHeader());
        httpPost.setHeader("Content-Type", "application/json");

        // Add custom headers
        headers.forEach(httpPost::setHeader);

        // Set body
        String jsonBody = gson.toJson(body);
        httpPost.setEntity(new StringEntity(jsonBody, StandardCharsets.UTF_8));

        return executeRequest(httpPost);
    }

    public String put(String path, Object body) throws IOException {
        String url = buildUrl(path);
        HttpPut httpPut = new HttpPut(url);

        // Add OAuth token
        AccessToken token = tokenManager.getAccessToken();
        httpPut.setHeader("Authorization", token.getAuthorizationHeader());
        httpPut.setHeader("Content-Type", "application/json");

        // Set body
        String jsonBody = gson.toJson(body);
        httpPut.setEntity(new StringEntity(jsonBody, StandardCharsets.UTF_8));

        return executeRequest(httpPut);
    }

    public String delete(String path) throws IOException {
        String url = buildUrl(path);
        HttpDelete httpDelete = new HttpDelete(url);

        // Add OAuth token
        AccessToken token = tokenManager.getAccessToken();
        httpDelete.setHeader("Authorization", token.getAuthorizationHeader());

        return executeRequest(httpDelete);
    }

    private String executeRequest(ClassicHttpRequest request) throws IOException {
        System.out.println("Executing: " + request.getMethod() + " " + request.getUri());

        try (CloseableHttpResponse response = httpClient.execute(request)) {
            int statusCode = response.getCode();
            String responseBody = response.getEntity() != null
                ? EntityUtils.toString(response.getEntity())
                : "";

            System.out.println("Response status: " + statusCode);

            if (statusCode >= 400) {
                throw new IOException("Request failed with status " + statusCode + ": " + responseBody);
            }

            return responseBody;
        }
    }

    private String buildUrl(String path) {
        if (path.startsWith("http://") || path.startsWith("https://")) {
            return path;
        }
        return baseUrl + (path.startsWith("/") ? path : "/" + path);
    }

    public <T> T get(String path, Class<T> responseType) throws IOException {
        String response = get(path);
        return gson.fromJson(response, responseType);
    }

    public <T> T post(String path, Object body, Class<T> responseType) throws IOException {
        String response = post(path, body);
        return gson.fromJson(response, responseType);
    }

    public void close() throws IOException {
        tokenManager.close();
        httpClient.close();
    }
}

// Mock OAuth Server for demonstration
class MockOAuthServer {
    public static String generateMockToken() {
        return "mock_access_token_" + UUID.randomUUID().toString().substring(0, 8);
    }

    public static String simulateTokenEndpoint(OAuth2Config config) {
        // Simulate OAuth token response
        JsonObject response = new JsonObject();
        response.addProperty("access_token", generateMockToken());
        response.addProperty("token_type", "Bearer");
        response.addProperty("expires_in", 3600);
        response.addProperty("scope", config.getScope());

        return new Gson().toJson(response);
    }
}

public class OAuth2RestClientApp {

    public static void main(String[] args) {
        System.out.println("=== OAuth 2.0 REST Client Demo ===\n");

        // Example 1: Client Credentials Flow
        System.out.println("--- Example 1: Client Credentials Flow ---");
        OAuth2Config clientCredsConfig = new OAuth2Config(
            "https://oauth.example.com/token",
            "my-client-id",
            "my-client-secret",
            "client_credentials"
        );
        clientCredsConfig.setScope("read:api write:api");

        System.out.println("Config:");
        System.out.println("  Token URL: " + clientCredsConfig.getTokenUrl());
        System.out.println("  Client ID: " + clientCredsConfig.getClientId());
        System.out.println("  Grant Type: " + clientCredsConfig.getGrantType());
        System.out.println("  Scope: " + clientCredsConfig.getScope());

        // Example 2: Password Grant Flow
        System.out.println("\n--- Example 2: Password Grant Flow ---");
        OAuth2Config passwordConfig = new OAuth2Config(
            "https://oauth.example.com/token",
            "my-client-id",
            "my-client-secret",
            "password"
        );
        passwordConfig.setUsername("user@example.com");
        passwordConfig.setPassword("user-password");
        passwordConfig.setScope("read:user write:user");

        System.out.println("Config:");
        System.out.println("  Token URL: " + passwordConfig.getTokenUrl());
        System.out.println("  Client ID: " + passwordConfig.getClientId());
        System.out.println("  Grant Type: " + passwordConfig.getGrantType());
        System.out.println("  Username: " + passwordConfig.getUsername());
        System.out.println("  Scope: " + passwordConfig.getScope());

        // Example 3: Token Manager Demo
        System.out.println("\n--- Example 3: Token Expiration Handling ---");
        AccessToken mockToken = new AccessToken("mock_token_123", "Bearer", 3600);
        System.out.println("Token created: " + mockToken);
        System.out.println("Is expired: " + mockToken.isExpired());
        System.out.println("Authorization header: " + mockToken.getAuthorizationHeader());

        // Simulate expired token
        AccessToken expiredToken = new AccessToken("old_token_456", "Bearer", -100);
        System.out.println("\nExpired token: " + expiredToken);
        System.out.println("Is expired: " + expiredToken.isExpired());

        // Example 4: REST Client Usage
        System.out.println("\n--- Example 4: REST Client Usage ---");
        System.out.println("Example usage code:\n");

        String exampleCode = """
            // Initialize OAuth2 REST Client
            OAuth2Config config = new OAuth2Config(
                "https://api.example.com/oauth/token",
                "client-id",
                "client-secret",
                "client_credentials"
            );
            config.setScope("api:read api:write");

            OAuth2RestClient client = new OAuth2RestClient(
                "https://api.example.com/v1",
                config
            );

            try {
                // GET request
                String users = client.get("/users");
                System.out.println("Users: " + users);

                // POST request
                Map<String, Object> newUser = Map.of(
                    "name", "John Doe",
                    "email", "john@example.com"
                );
                String created = client.post("/users", newUser);
                System.out.println("Created: " + created);

                // PUT request
                Map<String, Object> updates = Map.of("name", "John Updated");
                String updated = client.put("/users/123", updates);

                // DELETE request
                client.delete("/users/123");

                // Typed response
                UserResponse user = client.get("/users/123", UserResponse.class);

            } finally {
                client.close();
            }
            """;

        System.out.println(exampleCode);

        // Example 5: Response Type Mapping
        System.out.println("\n--- Example 5: Response Type Mapping ---");
        System.out.println("Define response classes for type-safe responses:\n");

        String typeMappingCode = """
            // Response DTO
            class UserResponse {
                private String id;
                private String name;
                private String email;
                // getters and setters
            }

            // Type-safe API call
            UserResponse user = client.get("/users/123", UserResponse.class);
            System.out.println("User: " + user.getName());
            """;

        System.out.println(typeMappingCode);

        System.out.println("\n=== OAuth 2.0 REST Client Demo Complete ===");
        System.out.println("\nKey Features:");
        System.out.println("  ✓ Automatic token refresh");
        System.out.println("  ✓ Token expiration handling");
        System.out.println("  ✓ Multiple OAuth grant types");
        System.out.println("  ✓ Type-safe response mapping");
        System.out.println("  ✓ RESTful HTTP methods (GET, POST, PUT, DELETE)");
        System.out.println("  ✓ Custom headers support");
        System.out.println("  ✓ JSON serialization/deserialization");
    }
}
