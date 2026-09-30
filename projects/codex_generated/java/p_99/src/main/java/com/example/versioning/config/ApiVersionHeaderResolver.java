package com.example.versioning.config;

import jakarta.servlet.http.HttpServletRequest;

public class ApiVersionHeaderResolver {

    public static final String HEADER_NAME = "X-API-Version";

    private ApiVersionHeaderResolver() {
    }

    public static String resolve(HttpServletRequest request) {
        String value = request.getHeader(HEADER_NAME);
        return value == null || value.isBlank() ? null : value.trim();
    }
}
