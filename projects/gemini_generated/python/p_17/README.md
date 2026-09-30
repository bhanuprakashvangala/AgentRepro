# CSV Data Validation Script

This project is a Python script that validates data in a CSV file against a flexible, predefined schema using the `pandas` and `Cerberus` libraries.

## Features

- **Schema-Based Validation**: Uses a clear, Python-native schema defined with Cerberus to enforce data rules.
- **Rich Validation Rules**: The schema checks for data types, required fields, regex patterns, value ranges, and allowed values.
- **Self-Contained Demo**: Automatically generates a `sample_data.csv` file containing both valid and invalid rows to provide a clear demonstration of the validation logic.
- **Detailed Reporting**: Generates a `validation_report.txt` that provides a summary of the validation process and lists each invalid row, the data it contained, and the specific reason for the validation failure.

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

3.  **Run the script:**
    ```bash
    python csv_validator.py
    ```

## Output

When you run the script, it will:

1.  Create a `sample_data.csv` file (if it doesn't exist).
2.  Process the CSV and print its progress to the console.
3.  Generate a `validation_report.txt` file. This report will summarize the findings and detail the errors found in the sample data, for instance:

```
--- CSV Validation Report ---

Source File: sample_data.csv
...
--- Summary ---
Total Rows Processed: 7
Valid Rows: 2 (28.57%)
Invalid Rows: 5 (71.43%)

--- Detailed Error Report ---

- Row 4:
  Data: {"employee_id": "EMP-1003", ...}
  Errors:
    - Field 'employee_id': 'value does not match regex ''^EMP\\d{4}$'''

- Row 5:
  Data: {"department": "HR", ...}
  Errors:
    - Field 'department': 'unallowed value HR'

...
```
