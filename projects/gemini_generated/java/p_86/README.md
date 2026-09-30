# File Upload Service

This is a simple file upload service built with Spring Boot and Apache Commons FileUpload.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd file-upload-service
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

You can upload files by sending a POST request to `http://localhost:8080/upload` with a multipart form data.

**Example using cURL:**

```bash
curl -X POST -F "file=@/path/to/your/file.png" http://localhost:8080/upload
```

- Replace `/path/to/your/file.png` with the actual path to your file.
- The service only accepts PNG and JPG files.
- The maximum file size is 10MB.

**Successful Response:**

```
File uploaded successfully: your-file.png
```

**Error Response (Invalid File Type):**

```
Invalid file type. Only PNG and JPG are allowed.
```

Uploaded files will be stored in the `uploads` directory in the root of the project.
