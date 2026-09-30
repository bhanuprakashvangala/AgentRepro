package com.example.pdfservice.service;

import com.example.pdfservice.model.ReportTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import org.springframework.stereotype.Component;

@Component
public class TemplateLoader {

    private final ObjectMapper objectMapper;

    public TemplateLoader(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public ReportTemplate load(String templatePath) throws IOException {
        try (InputStream inputStream = getClass().getResourceAsStream(templatePath)) {
            if (inputStream == null) {
                throw new IOException("Template not found: " + templatePath);
            }
            return objectMapper.readValue(inputStream, ReportTemplate.class);
        }
    }
}
