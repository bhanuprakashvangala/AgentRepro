# CSV to Database Importer

This project demonstrates a CSV to database importer using Spring Boot, Apache Commons CSV, and JDBC.

## Requirements

- Java 8 or higher
- Maven

## How to Run

1. **Clone the project:**
   ```bash
   git clone <repository-url>
   cd csv-importer
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

### Upload CSV File

Send a POST request to `http://localhost:8080/csv/upload` with a multipart file containing your CSV data.

**Example using cURL:**

```bash
curl -X POST -F "file=@/path/to/your/sample.csv" http://localhost:8080/csv/upload
```

Replace `/path/to/your/sample.csv` with the actual path to your CSV file. You can use the `src/main/resources/sample.csv` file provided in the project.

**Successful Response:**

```
CSV file uploaded and data imported successfully!
```

### Get All Users

```bash
curl http://localhost:8080/csv/users
```

This will return the data that was imported from the CSV file.

### H2 Console

The H2 console is enabled for easy database inspection. You can access it at `http://localhost:8080/h2-console`.

- **JDBC URL:** `jdbc:h2:mem:testdb`
- **User Name:** `sa`
- **Password:** `password`
