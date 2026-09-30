# JSON Parser and Validator

This project demonstrates a JSON parser and validator using Spring Boot, Jackson, and `json-schema-validator`.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd json-parser-validator
   ```

2. **Build the project:**
   ```bash
   mvn clean install
   ```

3. **Run the application:**
   ```bash
   mvn spring-boot:run
   ```

The application will start on port 8080.

## Usage

### Parse JSON to Object

Send a POST request to `http://localhost:8080/json/parse` with a JSON body representing a `User` object.

**Example using cURL (Valid JSON):**

```bash
curl -X POST -H "Content-Type: application/json" -d \
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30
} http://localhost:8080/json/parse
```

**Successful Response:**

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30
}
```

**Example using cURL (Invalid JSON - malformed):**

```bash
curl -X POST -H "Content-Type: application/json" -d \
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "age": 30,
} http://localhost:8080/json/parse
```

**Error Response:**

```
Error parsing JSON: Unexpected character ('}' (code 125)): was expecting double-quote to start field name
 at [Source: (String)"{\n  \"name\": \"John Doe\",\n  \"email\": \"john.doe@example.com\",\n  \"age\": 30,\n}"; line: 5, column: 1]
```

### Validate JSON against Schema

Send a POST request to `http://localhost:8080/json/validate` with a JSON body.

**Example using cURL (Valid JSON):**

```bash
curl -X POST -H "Content-Type: application/json" -d \
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "age": 25
} http://localhost:8080/json/validate
```

**Successful Response:**

```
JSON is valid.
```

**Example using cURL (Invalid JSON - violates schema):**

```bash
curl -X POST -H "Content-Type: application/json" -d \
{
  "name": "J",
  "email": "invalid-email",
  "age": 150
} http://localhost:8080/json/validate
```

**Error Response:**

```json
[
  {
    "message": "string \"invalid-email\" is not a valid email format",
    "path": "$.email",
    "arguments": [
      "email"
    ],
    "keyword": "format"
  },
  {
    "message": "$.age: must be less than or equal to 120",
    "path": "$.age",
    "arguments": [
      120,
      150
    ],
    "keyword": "maximum"
  },
  {
    "message": "$.name: must be at least 2 characters long",
    "path": "$.name",
    "arguments": [
      2,
      1
    ],
    "keyword": "minLength"
  }
]
```
