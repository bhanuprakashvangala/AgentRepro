# File Upload Service

Spring Boot REST API that receives multipart file uploads using Apache Commons FileUpload, validates file types and sizes, stores files locally, and returns metadata about the uploaded file.

## Features
- Commons FileUpload parses `multipart/form-data` requests without relying on Spring's `MultipartFile`
- Configurable allowed content types and maximum file size
- Files stored in `uploads/` directory (configurable)
- JSON response includes file name, size, type, storage path, and upload timestamp
- Centralized error handling for validation and server errors

## Prerequisites
- Java 17 or newer
- Apache Maven 3.9+

## Configure
Adjust values in `src/main/resources/application.properties`:
```properties
app.storage.location=uploads
app.storage.max-file-size=5MB
app.storage.allowed-content-types=image/png,image/jpeg,application/pdf
```

## Build & Run
```bash
cd 1-GPT/p_86
mvn clean package
mvn spring-boot:run
```

The service listens on `http://localhost:8080`.

## Upload a File
Use `curl` with `multipart/form-data`:
```bash
curl -X POST http://localhost:8080/api/files/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/file.pdf"
```

Example success response:
```json
{
  "status": "uploaded",
  "fileName": "file-1697043590000.pdf",
  "contentType": "application/pdf",
  "size": 12345,
  "uploadedAt": "2023-10-11T12:00:00.123Z",
  "path": "/absolute/path/uploads/file-1697043590000.pdf"
}
```

Validation failures (e.g., unsupported content type or oversized file) return HTTP 400 with an error message.

## Storage
- Uploaded files are stored locally; ensure the application has write permissions for the configured directory.
- To integrate cloud storage, replace the `saveFile` implementation in `FileStorageService` with your provider SDK.

## Stop
Press `Ctrl+C` in the terminal running the application.
