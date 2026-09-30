package com.example.transformer;

import com.google.gson.*;
import com.opencsv.*;
import java.io.*;
import java.util.*;
import java.util.function.*;
import java.util.stream.Collectors;

interface Transformer<T> {
    T transform(T data);
}

class DataTransformer {

    // JSON to CSV
    public static String jsonToCsv(String jsonArray) {
        Gson gson = new Gson();
        JsonArray array = gson.fromJson(jsonArray, JsonArray.class);

        if (array.isEmpty()) {
            return "";
        }

        // Extract headers from first object
        JsonObject firstObj = array.get(0).getAsJsonObject();
        List<String> headers = new ArrayList<>();
        firstObj.keySet().forEach(headers::add);

        StringBuilder csv = new StringBuilder();

        // Write headers
        csv.append(String.join(",", headers)).append("\n");

        // Write rows
        for (JsonElement element : array) {
            JsonObject obj = element.getAsJsonObject();
            List<String> values = new ArrayList<>();

            for (String header : headers) {
                JsonElement value = obj.get(header);
                if (value == null || value.isJsonNull()) {
                    values.add("");
                } else {
                    values.add(escapeCSV(value.getAsString()));
                }
            }

            csv.append(String.join(",", values)).append("\n");
        }

        return csv.toString();
    }

    // CSV to JSON
    public static String csvToJson(String csvData) throws IOException {
        StringReader reader = new StringReader(csvData);
        CSVReader csvReader = new CSVReaderBuilder(reader).build();

        List<String[]> records = csvReader.readAll();
        if (records.isEmpty()) {
            return "[]";
        }

        String[] headers = records.get(0);
        JsonArray jsonArray = new JsonArray();

        for (int i = 1; i < records.size(); i++) {
            String[] row = records.get(i);
            JsonObject jsonObject = new JsonObject();

            for (int j = 0; j < headers.length && j < row.length; j++) {
                String value = row[j];

                // Try to detect number types
                if (value.matches("-?\\d+")) {
                    jsonObject.addProperty(headers[j], Long.parseLong(value));
                } else if (value.matches("-?\\d+\\.\\d+")) {
                    jsonObject.addProperty(headers[j], Double.parseDouble(value));
                } else if (value.equalsIgnoreCase("true") || value.equalsIgnoreCase("false")) {
                    jsonObject.addProperty(headers[j], Boolean.parseBoolean(value));
                } else {
                    jsonObject.addProperty(headers[j], value);
                }
            }

            jsonArray.add(jsonObject);
        }

        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        return gson.toJson(jsonArray);
    }

    private static String escapeCSV(String value) {
        if (value.contains(",") || value.contains("\"") || value.contains("\n")) {
            return "\"" + value.replace("\"", "\"\"") + "\"";
        }
        return value;
    }

    // Filter data
    public static JsonArray filter(JsonArray data, Predicate<JsonObject> predicate) {
        JsonArray filtered = new JsonArray();

        for (JsonElement element : data) {
            if (element.isJsonObject()) {
                JsonObject obj = element.getAsJsonObject();
                if (predicate.test(obj)) {
                    filtered.add(obj);
                }
            }
        }

        return filtered;
    }

    // Map/transform data
    public static JsonArray map(JsonArray data, Function<JsonObject, JsonObject> mapper) {
        JsonArray mapped = new JsonArray();

        for (JsonElement element : data) {
            if (element.isJsonObject()) {
                JsonObject transformed = mapper.apply(element.getAsJsonObject());
                mapped.add(transformed);
            }
        }

        return mapped;
    }

    // Rename fields
    public static JsonObject renameFields(JsonObject obj, Map<String, String> fieldMapping) {
        JsonObject renamed = new JsonObject();

        for (Map.Entry<String, JsonElement> entry : obj.entrySet()) {
            String oldName = entry.getKey();
            String newName = fieldMapping.getOrDefault(oldName, oldName);
            renamed.add(newName, entry.getValue());
        }

        return renamed;
    }

    // Select specific fields
    public static JsonObject selectFields(JsonObject obj, List<String> fields) {
        JsonObject selected = new JsonObject();

        for (String field : fields) {
            if (obj.has(field)) {
                selected.add(field, obj.get(field));
            }
        }

        return selected;
    }

    // Group by field and aggregate
    public static Map<String, List<JsonObject>> groupBy(JsonArray data, String field) {
        Map<String, List<JsonObject>> groups = new HashMap<>();

        for (JsonElement element : data) {
            if (element.isJsonObject()) {
                JsonObject obj = element.getAsJsonObject();
                if (obj.has(field)) {
                    String key = obj.get(field).getAsString();
                    groups.computeIfAbsent(key, k -> new ArrayList<>()).add(obj);
                }
            }
        }

        return groups;
    }

    // Aggregate functions
    public static double sum(JsonArray data, String field) {
        return data.asList().stream()
            .filter(e -> e.isJsonObject())
            .map(e -> e.getAsJsonObject())
            .filter(obj -> obj.has(field))
            .mapToDouble(obj -> obj.get(field).getAsDouble())
            .sum();
    }

    public static double average(JsonArray data, String field) {
        return data.asList().stream()
            .filter(e -> e.isJsonObject())
            .map(e -> e.getAsJsonObject())
            .filter(obj -> obj.has(field))
            .mapToDouble(obj -> obj.get(field).getAsDouble())
            .average()
            .orElse(0.0);
    }

    public static long count(JsonArray data, Predicate<JsonObject> predicate) {
        return data.asList().stream()
            .filter(e -> e.isJsonObject())
            .map(e -> e.getAsJsonObject())
            .filter(predicate)
            .count();
    }
}

class TransformationPipeline {
    private JsonArray data;
    private final List<Function<JsonArray, JsonArray>> transformations = new ArrayList<>();

    public TransformationPipeline(JsonArray initialData) {
        this.data = initialData;
    }

    public TransformationPipeline filter(Predicate<JsonObject> predicate) {
        transformations.add(arr -> DataTransformer.filter(arr, predicate));
        return this;
    }

    public TransformationPipeline map(Function<JsonObject, JsonObject> mapper) {
        transformations.add(arr -> DataTransformer.map(arr, mapper));
        return this;
    }

    public TransformationPipeline renameFields(Map<String, String> fieldMapping) {
        transformations.add(arr ->
            DataTransformer.map(arr, obj -> DataTransformer.renameFields(obj, fieldMapping))
        );
        return this;
    }

    public TransformationPipeline selectFields(List<String> fields) {
        transformations.add(arr ->
            DataTransformer.map(arr, obj -> DataTransformer.selectFields(obj, fields))
        );
        return this;
    }

    public TransformationPipeline sortBy(String field, boolean ascending) {
        transformations.add(arr -> {
            List<JsonElement> list = new ArrayList<>();
            arr.forEach(list::add);

            list.sort((a, b) -> {
                JsonObject objA = a.getAsJsonObject();
                JsonObject objB = b.getAsJsonObject();

                if (!objA.has(field) || !objB.has(field)) return 0;

                String valA = objA.get(field).getAsString();
                String valB = objB.get(field).getAsString();

                return ascending ? valA.compareTo(valB) : valB.compareTo(valA);
            });

            JsonArray sorted = new JsonArray();
            list.forEach(sorted::add);
            return sorted;
        });
        return this;
    }

    public TransformationPipeline limit(int count) {
        transformations.add(arr -> {
            JsonArray limited = new JsonArray();
            for (int i = 0; i < Math.min(count, arr.size()); i++) {
                limited.add(arr.get(i));
            }
            return limited;
        });
        return this;
    }

    public JsonArray execute() {
        JsonArray result = data;
        for (Function<JsonArray, JsonArray> transformation : transformations) {
            result = transformation.apply(result);
        }
        return result;
    }
}

class DataValidator {
    public static boolean validateEmail(String email) {
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$");
    }

    public static boolean validateRequired(JsonObject obj, List<String> requiredFields) {
        return requiredFields.stream().allMatch(obj::has);
    }

    public static boolean validateType(JsonObject obj, String field, Class<?> expectedType) {
        if (!obj.has(field)) return false;

        JsonElement element = obj.get(field);

        if (expectedType == String.class) return element.isJsonPrimitive();
        if (expectedType == Integer.class || expectedType == Long.class) {
            return element.isJsonPrimitive() && element.getAsJsonPrimitive().isNumber();
        }
        if (expectedType == Boolean.class) {
            return element.isJsonPrimitive() && element.getAsJsonPrimitive().isBoolean();
        }

        return false;
    }

    public static List<String> validate(JsonArray data, Predicate<JsonObject> validator) {
        List<String> errors = new ArrayList<>();

        for (int i = 0; i < data.size(); i++) {
            if (data.get(i).isJsonObject()) {
                JsonObject obj = data.get(i).getAsJsonObject();
                if (!validator.test(obj)) {
                    errors.add("Validation failed for record at index " + i);
                }
            }
        }

        return errors;
    }
}

public class DataTransformerApp {

    public static void main(String[] args) {
        System.out.println("=== Data Transformation Utility ===\n");
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        // Sample data
        String jsonData = """
            [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 75000, "age": 28},
                {"id": 2, "name": "Bob", "department": "Sales", "salary": 65000, "age": 35},
                {"id": 3, "name": "Charlie", "department": "Engineering", "salary": 85000, "age": 32},
                {"id": 4, "name": "Diana", "department": "Marketing", "salary": 70000, "age": 29},
                {"id": 5, "name": "Eve", "department": "Engineering", "salary": 95000, "age": 40}
            ]
            """;

        JsonArray employees = gson.fromJson(jsonData, JsonArray.class);

        // Example 1: JSON to CSV
        System.out.println("--- Example 1: JSON to CSV ---");
        String csv = DataTransformer.jsonToCsv(jsonData);
        System.out.println("CSV Output:");
        System.out.println(csv);

        // Example 2: CSV to JSON
        System.out.println("--- Example 2: CSV to JSON ---");
        try {
            String jsonFromCsv = DataTransformer.csvToJson(csv);
            System.out.println("JSON from CSV:");
            System.out.println(jsonFromCsv);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Example 3: Filtering
        System.out.println("\n--- Example 3: Filtering ---");
        JsonArray engineeringOnly = DataTransformer.filter(employees,
            obj -> obj.get("department").getAsString().equals("Engineering"));
        System.out.println("Engineering employees:");
        System.out.println(gson.toJson(engineeringOnly));

        JsonArray highEarners = DataTransformer.filter(employees,
            obj -> obj.get("salary").getAsDouble() >= 75000);
        System.out.println("\nHigh earners (>= $75,000):");
        System.out.println(gson.toJson(highEarners));

        // Example 4: Mapping/Transformation
        System.out.println("\n--- Example 4: Field Transformation ---");
        JsonArray transformed = DataTransformer.map(employees, obj -> {
            JsonObject newObj = new JsonObject();
            newObj.addProperty("employee_id", obj.get("id").getAsInt());
            newObj.addProperty("full_name", obj.get("name").getAsString().toUpperCase());
            newObj.addProperty("dept", obj.get("department").getAsString());
            newObj.addProperty("annual_salary", obj.get("salary").getAsDouble() * 1.1); // 10% raise
            return newObj;
        });
        System.out.println("Transformed data:");
        System.out.println(gson.toJson(transformed));

        // Example 5: Field renaming
        System.out.println("\n--- Example 5: Field Renaming ---");
        Map<String, String> fieldMapping = Map.of(
            "id", "employee_id",
            "name", "full_name",
            "department", "dept"
        );

        JsonArray renamed = DataTransformer.map(employees,
            obj -> DataTransformer.renameFields(obj, fieldMapping));
        System.out.println("Renamed fields:");
        System.out.println(gson.toJson(renamed));

        // Example 6: Field selection
        System.out.println("\n--- Example 6: Field Selection ---");
        JsonArray selected = DataTransformer.map(employees,
            obj -> DataTransformer.selectFields(obj, List.of("name", "salary")));
        System.out.println("Selected fields (name, salary only):");
        System.out.println(gson.toJson(selected));

        // Example 7: Grouping
        System.out.println("\n--- Example 7: Group By ---");
        Map<String, List<JsonObject>> byDepartment = DataTransformer.groupBy(employees, "department");
        System.out.println("Employees by department:");
        byDepartment.forEach((dept, emps) -> {
            System.out.println("  " + dept + ": " + emps.size() + " employees");
        });

        // Example 8: Aggregations
        System.out.println("\n--- Example 8: Aggregations ---");
        double totalSalary = DataTransformer.sum(employees, "salary");
        double avgSalary = DataTransformer.average(employees, "salary");
        long engineerCount = DataTransformer.count(employees,
            obj -> obj.get("department").getAsString().equals("Engineering"));

        System.out.println("Total salary: $" + totalSalary);
        System.out.println("Average salary: $" + avgSalary);
        System.out.println("Engineers: " + engineerCount);

        // Example 9: Transformation Pipeline
        System.out.println("\n--- Example 9: Transformation Pipeline ---");
        JsonArray pipelineResult = new TransformationPipeline(employees)
            .filter(obj -> obj.get("salary").getAsDouble() >= 70000)
            .selectFields(List.of("name", "department", "salary"))
            .sortBy("salary", false)
            .limit(3)
            .execute();

        System.out.println("Top 3 high earners (>= $70k):");
        System.out.println(gson.toJson(pipelineResult));

        // Example 10: Validation
        System.out.println("\n--- Example 10: Data Validation ---");
        List<String> requiredFields = List.of("id", "name", "department");
        List<String> validationErrors = DataValidator.validate(employees,
            obj -> DataValidator.validateRequired(obj, requiredFields));

        if (validationErrors.isEmpty()) {
            System.out.println("All records valid!");
        } else {
            System.out.println("Validation errors:");
            validationErrors.forEach(System.out::println);
        }

        System.out.println("\n=== Data Transformation Demo Complete ===");
    }
}
