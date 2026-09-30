# CSV to JSON Converter API

This project is a CSV to JSON converter API built with Express, Multer, and csv-parser.

## Requirements

- Node.js
- npm

## Installation

1.  Install the dependencies:

    ```bash
    npm install
    ```

## Usage

1.  Start the server:

    ```bash
    npm start
    ```

2.  Send a POST request to `http://localhost:3000/convert` with a `multipart/form-data` payload.

### Form Fields

-   `file`: The CSV file to convert.
-   `delimiter` (optional): The CSV delimiter (default: `,`).
-   `headers` (optional): A comma-separated list of custom headers.

### Example

```bash
curl -X POST -F "file=@/path/to/your/file.csv" -F "delimiter=;" http://localhost:3000/convert
```
