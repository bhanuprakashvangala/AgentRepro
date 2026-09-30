package com.example.jsonvalidator.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.stream.Collectors;
import org.everit.json.schema.Schema;
import org.everit.json.schema.ValidationException;
import org.everit.json.schema.loader.SchemaLoader;
import org.json.JSONObject;
import org.json.JSONTokener;
import org.springframework.stereotype.Service;

@Service
public class JsonValidationService {

    private final ObjectMapper objectMapper;

    public JsonValidationService(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public Object parse(String json) throws IOException {
        JsonNode node = objectMapper.readTree(json);
        return objectMapper.treeToValue(node, Object.class);
    }

    public List<String> validate(String schemaName, String json) throws IOException {
        Schema schema = loadSchema(schemaName);
        try {
            schema.validate(new JSONObject(json));
            return List.of();
        } catch (ValidationException ex) {
            return ex.getAllMessages();
        }
    }

    private Schema loadSchema(String schemaName) throws IOException {
        String path = "/schemas/" + schemaName + ".json";
        try (InputStream inputStream = getClass().getResourceAsStream(path)) {
            if (inputStream == null) {
                throw new IOException("Schema not found: " + schemaName);
            }
            JSONObject rawSchema = new JSONObject(new JSONTokener(inputStream));
            return SchemaLoader.load(rawSchema);
        }
    }
}
