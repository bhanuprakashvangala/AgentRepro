# JSON to CSV Converter

Flattens nested JSON payloads into normalized CSV using pandas.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python json_to_csv.py --input data.json --output data.csv
```

Options:
- `--orient`: `records` (default) treats the root as a list of objects or a single object. `list` expects an object with a list under `--root-key`.
- `--root-key`: Required when `--orient=list`; specifies the key containing records.
- `--sep`: Separator for flattened column names (default `.`).
- `--explode`: Optional columns to explode if they contain arrays (creates multiple rows per value).

Example:
```bash
python json_to_csv.py --input nested.json --output flattened.csv --sep "_" --explode items
```

This command loads `nested.json`, flattens nested objects/arrays into column values, expands the `items` array into multiple rows, and writes the normalized CSV.
