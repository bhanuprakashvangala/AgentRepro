# JSON to CSV Converter

This is a command-line tool that converts complex, nested JSON files into a single, flat CSV file using the `pandas` library.

## Features

- **Nested Object Flattening**: Automatically flattens nested JSON objects (e.g., an `address` object) into separate columns (e.g., `address_street`, `address_city`).
- **Array Unpacking**: Expands items from a nested array (e.g., a list of `orders`) into their own rows, while repeating the parent-level data for each new row.
- **Reproducible Demo**: Includes a `--demo` mode that generates a complex `sample.json` file and converts it, allowing you to test the functionality instantly.
- **Powered by Pandas**: Uses the powerful and efficient `pandas.json_normalize` function to handle the conversion.

## How it Works

The script is designed to handle JSON structures where you have a main list of records (e.g., users), and each record contains a nested list of sub-records (e.g., orders). The `json_normalize` function is configured with a `record_path` to identify the nested list to "unwind" into rows, and a `meta` configuration to carry over the parent data to each new row.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Recommended) Run the Demo:**
    This is the easiest way to see the tool in action. It will create `sample.json` and then convert it to `output.csv`.
    ```bash
    python json_to_csv.py --demo
    ```

4.  **Convert Your Own File:**
    Use the `--input` and `--output` flags to specify your files.
    ```bash
    python json_to_csv.py --input your_data.json --output your_data.csv
    ```

## Example Conversion

The demo will convert a `sample.json` file that looks like this:
```json
[
    {
        "id": 1,
        "name": "John Doe",
        "address": {
            "street": "123 Main St",
            "city": "Anytown"
        },
        "orders": [
            {"order_id": "A101", "amount": 150.75, ...},
            {"order_id": "A102", "amount": 200.00, ...}
        ]
    }, ...
]
```

...into a flat `output.csv` file that looks like this:

```csv
id,name,email,address_street,address_city,order_id,amount,date
1,John Doe,john.doe@example.com,123 Main St,Anytown,A101,150.75,2023-01-15
1,John Doe,john.doe@example.com,123 Main St,Anytown,A102,200.0,2023-02-20
2,Jane Smith,jane.smith@example.com,456 Oak Ave,Someville,B201,300.5,2023-03-10
```
