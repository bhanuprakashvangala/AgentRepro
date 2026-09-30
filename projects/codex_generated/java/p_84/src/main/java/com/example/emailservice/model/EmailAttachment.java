package com.example.emailservice.model;

import jakarta.validation.constraints.NotBlank;

public class EmailAttachment {

    @NotBlank
    private String fileName;

    @NotBlank
    private String contentType;

    /**
     * Base64 encoded file content.
     */
    @NotBlank
    private String base64Data;

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getContentType() {
        return contentType;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public String getBase64Data() {
        return base64Data;
    }

    public void setBase64Data(String base64Data) {
        this.base64Data = base64Data;
    }
}

