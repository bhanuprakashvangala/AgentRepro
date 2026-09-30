# CSV Schema Validator

Validates CSV data against a JSON Schema using pandas for ingestion and `jsonschema` for row-level checks. Produces a detailed JSON report and a CSV of invalid rows with failure reasons.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Prepare a JSON Schema

Example (`schema.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["id", "email", "age"],
  "properties": {
    "id": {"type": "integer", "minimum": 1},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "minimum": 18, "maximum": 99},
    "signup_date": {"type": "string", "format": "date"}
  }
}
```

## Run validation

```bash
python validate_csv.py \
  --csv data.csv \
  --schema schema.json \
  --report validation_report.json \
  --invalid-csv invalid_rows.csv
```

### Options
- `--encoding`: CSV encoding (default `utf-8`).
- `--index-column`: Column to use as row identifier in reports (defaults to row number).

## Output
- `validation_report.json`: Summary totals, aggregated error messages with counts, and per-row details for every failure.
- `invalid_rows.csv`: Original column values for invalid records plus `__validation_errors` and `__row_identifier` columns describing issues.

Use JSON Schema constraints (types, `minimum`, `maximum`, `format`, etc.) to enforce data quality rules. The script reports all violations per row so you can correct data cleanly.
