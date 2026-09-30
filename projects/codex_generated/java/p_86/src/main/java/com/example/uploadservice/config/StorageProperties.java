package com.example.uploadservice.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.util.unit.DataSize;

@ConfigurationProperties(prefix = "app.storage")
public class StorageProperties {

    /**
     * Directory where uploaded files are stored.
     */
    private String location = "uploads";

    /**
     * Maximum allowed file size.
     */
    private DataSize maxFileSize = DataSize.ofMegabytes(5);

    /**
     * Allowed content types (comma separated).
     */
    private String[] allowedContentTypes = new String[]{"image/png", "image/jpeg", "application/pdf"};

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public DataSize getMaxFileSize() {
        return maxFileSize;
    }

    public void setMaxFileSize(DataSize maxFileSize) {
        this.maxFileSize = maxFileSize;
    }

    public String[] getAllowedContentTypes() {
        return allowedContentTypes;
    }

    public void setAllowedContentTypes(String[] allowedContentTypes) {
        this.allowedContentTypes = allowedContentTypes;
    }
}
