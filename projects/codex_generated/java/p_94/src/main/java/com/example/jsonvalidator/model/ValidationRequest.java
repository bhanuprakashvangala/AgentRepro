package com.example.jsonvalidator.model;

import jakarta.validation.constraints.NotBlank;

public class ValidationRequest {

    @NotBlank(message = "Schema name is required")
    private String schemaName;

    @NotBlank(message = "JSON payload is required")
    private String json;

    public String getSchemaName() {
        return schemaName;
    }

    public void setSchemaName(String schemaName) {
        this.schemaName = schemaName;
    }

    public String getJson() {
        return json;
    }

    public void setJson(String json) {
        this.json = json;
    }
}
