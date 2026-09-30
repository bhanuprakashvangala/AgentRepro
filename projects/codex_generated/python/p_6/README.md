# CSV to SQLite ETL Pipeline

This script extracts data from a CSV file, cleans and transforms it with pandas, then loads the result into a SQLite database using SQLAlchemy. It also produces a JSON summary report for quick insight into numeric and categorical columns.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python etl_pipeline.py --input data.csv --database etl_output.db --table records --summary summary.json
```

Options:
- `--input`: Path to the source CSV file (required).
- `--database`: SQLite database file to create or update (default `etl_output.db`).
- `--table`: Target table name in SQLite (default `records`).
- `--summary`: Where to write the JSON summary report (default `summary.json`).
- `--if-exists`: Table handling strategy (`fail`, `replace`, `append`; default `replace`).
- `--encoding`: CSV encoding (default `utf-8`).

The script drops duplicate rows, fills numeric gaps with medians, fills categorical gaps with `"Unknown"`, and defaults datetime gaps to `1970-01-01`. The resulting SQLite table contains the cleaned data, while the summary JSON holds descriptive statistics for numeric columns and the top 5 value counts for categorical columns.
