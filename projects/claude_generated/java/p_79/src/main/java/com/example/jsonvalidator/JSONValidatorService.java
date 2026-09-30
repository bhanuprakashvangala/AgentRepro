package com.example.jsonvalidator;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.everit.json.schema.Schema;
import org.everit.json.schema.ValidationException;
import org.everit.json.schema.loader.SchemaLoader;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.IOException;
import java.util.*;

public class JSONValidatorService {
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Map<String, Schema> schemas = new HashMap<>();

    public JSONValidatorService() {
        initializeSchemas();
    }

    private void initializeSchemas() {
        // User schema
        String userSchema = """
            {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "active": {"type": "boolean"}
              },
              "required": ["name", "email"]
            }
            """;

        // Product schema
        String productSchema = """
            {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "id": {"type": "string"},
                "name": {"type": "string", "minLength": 1},
                "price": {"type": "number", "minimum": 0},
                "category": {"type": "string"},
                "inStock": {"type": "boolean"}
              },
              "required": ["name", "price"]
            }
            """;

        // Order schema
        String orderSchema = """
            {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "orderId": {"type": "string"},
                "customerId": {"type": "string"},
                "items": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "productId": {"type": "string"},
                      "quantity": {"type": "integer", "minimum": 1},
                      "price": {"type": "number", "minimum": 0}
                    },
                    "required": ["productId", "quantity", "price"]
                  },
                  "minItems": 1
                },
                "totalAmount": {"type": "number", "minimum": 0}
              },
              "required": ["orderId", "customerId", "items", "totalAmount"]
            }
            """;

        registerSchema("user", userSchema);
        registerSchema("product", productSchema);
        registerSchema("order", orderSchema);
    }

    public void registerSchema(String schemaName, String schemaJson) {
        JSONObject rawSchema = new JSONObject(new JSONTokener(schemaJson));
        Schema schema = SchemaLoader.load(rawSchema);
        schemas.put(schemaName, schema);
        System.out.println("Schema registered: " + schemaName);
    }

    public ValidationResult validate(String schemaName, String jsonData) {
        if (!schemas.containsKey(schemaName)) {
            return ValidationResult.error("Schema not found: " + schemaName);
        }

        Schema schema = schemas.get(schemaName);
        ValidationResult result = new ValidationResult();

        try {
            JSONObject jsonObject = new JSONObject(new JSONTokener(jsonData));
            schema.validate(jsonObject);
            result.setValid(true);
            result.setMessage("Validation successful");
        } catch (ValidationException e) {
            result.setValid(false);
            result.setMessage("Validation failed");
            result.setErrors(collectErrors(e));
        } catch (Exception e) {
            result.setValid(false);
            result.setMessage("Invalid JSON: " + e.getMessage());
        }

        return result;
    }

    private List<String> collectErrors(ValidationException e) {
        List<String> errors = new ArrayList<>();
        errors.add(e.getMessage());
        e.getCausingExceptions().forEach(ex -> errors.add(ex.getMessage()));
        return errors;
    }

    public Set<String> getRegisteredSchemas() {
        return schemas.keySet();
    }

    // Example usage
    public static void main(String[] args) {
        JSONValidatorService validator = new JSONValidatorService();

        // Test 1: Valid user
        String validUser = """
            {
              "name": "John Doe",
              "email": "john@example.com",
              "age": 30,
              "active": true
            }
            """;

        ValidationResult result1 = validator.validate("user", validUser);
        System.out.println("\nTest 1 - Valid User:");
        System.out.println("Valid: " + result1.isValid());
        System.out.println("Message: " + result1.getMessage());

        // Test 2: Invalid user (missing required email)
        String invalidUser = """
            {
              "name": "Jane Doe",
              "age": 25
            }
            """;

        ValidationResult result2 = validator.validate("user", invalidUser);
        System.out.println("\nTest 2 - Invalid User:");
        System.out.println("Valid: " + result2.isValid());
        System.out.println("Message: " + result2.getMessage());
        System.out.println("Errors: " + result2.getErrors());

        // Test 3: Valid product
        String validProduct = """
            {
              "id": "P123",
              "name": "Laptop",
              "price": 999.99,
              "category": "Electronics",
              "inStock": true
            }
            """;

        ValidationResult result3 = validator.validate("product", validProduct);
        System.out.println("\nTest 3 - Valid Product:");
        System.out.println("Valid: " + result3.isValid());

        // Test 4: Valid order
        String validOrder = """
            {
              "orderId": "ORD-001",
              "customerId": "CUST-123",
              "items": [
                {
                  "productId": "P123",
                  "quantity": 2,
                  "price": 999.99
                },
                {
                  "productId": "P456",
                  "quantity": 1,
                  "price": 299.99
                }
              ],
              "totalAmount": 2299.97
            }
            """;

        ValidationResult result4 = validator.validate("order", validOrder);
        System.out.println("\nTest 4 - Valid Order:");
        System.out.println("Valid: " + result4.isValid());

        // Test 5: Invalid order (negative price)
        String invalidOrder = """
            {
              "orderId": "ORD-002",
              "customerId": "CUST-456",
              "items": [
                {
                  "productId": "P789",
                  "quantity": 1,
                  "price": -50.00
                }
              ],
              "totalAmount": -50.00
            }
            """;

        ValidationResult result5 = validator.validate("order", invalidOrder);
        System.out.println("\nTest 5 - Invalid Order:");
        System.out.println("Valid: " + result5.isValid());
        System.out.println("Errors: " + result5.getErrors());

        System.out.println("\nRegistered schemas: " + validator.getRegisteredSchemas());
    }
}

class ValidationResult {
    private boolean valid;
    private String message;
    private List<String> errors = new ArrayList<>();

    public static ValidationResult error(String message) {
        ValidationResult result = new ValidationResult();
        result.setValid(false);
        result.setMessage(message);
        return result;
    }

    public boolean isValid() { return valid; }
    public void setValid(boolean valid) { this.valid = valid; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public List<String> getErrors() { return errors; }
    public void setErrors(List<String> errors) { this.errors = errors; }

    @Override
    public String toString() {
        return "ValidationResult{valid=" + valid + ", message='" + message + "', errors=" + errors + "}";
    }
}
