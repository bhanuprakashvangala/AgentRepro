# PDF Generation Service

This is a simple PDF generation service built with Spring Boot, iText, and Thymeleaf.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd pdf-generation-service
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

You can generate a PDF by sending a GET request to `http://localhost:8080/generate-pdf`.

You can also provide `name` and `course` as request parameters to customize the PDF.

**Example using a web browser:**

Open the following URL in your browser:

```
http://localhost:8080/generate-pdf?name=Jane%20Doe&course=iText%20PDF%20Generation
```

This will download a PDF file named `generated-pdf.pdf`.

**Example using cURL:**

```bash
curl -o generated-pdf.pdf http://localhost:8080/generate-pdf?name=Jane%20Doe&course=iText%20PDF%20Generation
```
