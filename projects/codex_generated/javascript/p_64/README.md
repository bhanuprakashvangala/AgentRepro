# CSV → JSON Converter API

Express service that streams CSV files to JSON responses using `csv-parser`. Supports custom delimiters, optional headers, data type coercion, and skips initial lines. Designed for large files via streaming.

## Setup
```bash
npm install
npm start
```
Server runs on `http://localhost:4000` (override with `PORT`).

## API
`POST /convert`
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required) – CSV upload
  - `delimiter` (optional, default `,`)
  - `headers` (`true`|`false`|`["h1","h2"]`)
  - `types` (JSON mapping field→type, e.g. `{ "price": "number", "createdAt": "date" }`)
  - `skipLines` (number)

Response is streamed JSON array. Append `types` to coerce numbers, booleans, dates (to ISO strings).

Example using curl:
```bash
curl -F "file=@data.csv" -F "delimiter=;" -F "types={\"amount\":\"number\"}" http://localhost:4000/convert
```
