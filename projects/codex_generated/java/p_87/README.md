# PDF Generation Service

Spring Boot service that renders polished PDF reports using Apache PDFBox and a JSON-based layout template. The generated documents include branded headers, tables, custom colors, and a generated logo image.

## Features
- Apache PDFBox for low-level PDF creation
- JSON template (`src/main/resources/templates/report-template.json`) describing fonts, colors, columns, and layout
- Support for images (runtime-generated logo), multi-column tables, and styled sections
- REST API to generate PDFs from posted data or download a ready-made sample

## Prerequisites
- Java 17 or newer
- Apache Maven 3.9+

## Install & Run
```bash
cd 1-GPT/p_87
mvn clean package
mvn spring-boot:run
```

The API listens on `http://localhost:8080`.

## Endpoints

### `POST /api/pdf/generate`
Generate a PDF from a JSON payload matching `ReportRequest`:
```bash
curl -X POST http://localhost:8080/api/pdf/generate \
  -H "Content-Type: application/json" \
  --output report.pdf \
  -d '{
        "title":"Project Summary",
        "subtitle":"June 2024 Deliverables",
        "preparedFor":"Globex Corporation",
        "preparedBy":"Acme Analytics",
        "items":[
          {"item":"Discovery Workshop","description":"On-site discovery with key stakeholders.","quantity":2,"unitPrice":850.00},
          {"item":"Prototype","description":"Interactive prototype with stakeholder feedback loop.","quantity":1,"unitPrice":1200.00}
        ],
        "notes":"Draft generated via PDFBox template."
      }'
```
The response is an `application/pdf` document containing the rendered report.

### `GET /api/pdf/sample`
Downloads a pre-configured sample report demonstrating headers, tables, and styling:
```bash
curl -L http://localhost:8080/api/pdf/sample --output sample-report.pdf
```

### `GET /api/pdf/template`
Returns metadata describing required fields and usage notes for the template.

## Customisation
- Edit `report-template.json` to tweak margins, column widths, fonts, and colors.
- The generated logo is created with Java2D; adjust brand text or styling by updating the template’s `logo` section.
- Extend `PdfReportService` to add additional sections such as charts or multi-page logic.

## Stop
Quit the Spring Boot app with `Ctrl+C` in the terminal.
