package com.example.jsonparser;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Set;

@Service
public class JsonValidationService {

    private final ObjectMapper objectMapper;
    private final JsonSchema userSchema;

    public JsonValidationService(ObjectMapper objectMapper) throws IOException {
        this.objectMapper = objectMapper;
        JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
        try (InputStream is = getClass().getResourceAsStream("/user-schema.json")) {
            this.userSchema = factory.getSchema(is);
        }
    }

    public <T> T parseJson(String jsonString, Class<T> valueType) throws IOException {
        return objectMapper.readValue(jsonString, valueType);
    }

    public Set<ValidationMessage> validateJson(String jsonString) throws IOException {
        JsonNode jsonNode = objectMapper.readTree(jsonString);
        return userSchema.validate(jsonNode);
    }
}
