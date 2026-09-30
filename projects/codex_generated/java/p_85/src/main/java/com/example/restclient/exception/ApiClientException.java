package com.example.restclient.exception;

import org.springframework.http.HttpStatusCode;

public class ApiClientException extends RuntimeException {

    private final HttpStatusCode statusCode;
    private final String responseBody;

    public ApiClientException(String message, HttpStatusCode statusCode, String responseBody, Throwable cause) {
        super(message, cause);
        this.statusCode = statusCode;
        this.responseBody = responseBody;
    }

    public HttpStatusCode getStatusCode() {
        return statusCode;
    }

    public String getResponseBody() {
        return responseBody;
    }
}
