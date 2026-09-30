import pandas as pd
from cerberus import Validator
import os
import csv
from datetime import datetime

CSV_FILE = "sample_data.csv"
REPORT_FILE = "validation_report.txt"

def generate_sample_csv(filename=CSV_FILE):
    """Generates a sample CSV with both valid and invalid data for demonstration."""
    if os.path.exists(filename):
        print(f"Sample CSV '{filename}' already exists.")
        return

    print(f"Generating sample CSV with valid and invalid rows: {filename}")
    data = [
        ['employee_id', 'name', 'email', 'department', 'salary', 'hire_date'],
        # Valid rows
        ['EMP1001', 'John Doe', 'john.doe@example.com', 'Engineering', '90000', '2022-01-15'],
        ['EMP1002', 'Jane Smith', 'jane.smith@example.com', 'Marketing', '75000', '2021-03-20'],
        # Invalid rows
        ['EMP-1003', 'Peter Jones', 'peter.jones@example.com', 'Engineering', '80000', '2023-05-10'], # Invalid employee_id format
        ['EMP1004', 'Mary Davis', 'mary.davis@example.com', 'HR', '65000', '2022-11-01'],          # Invalid department
        ['EMP1005', 'Chris Lee', 'chris.lee', 'Sales', '72000', '2023-01-20'],                 # Invalid email format
        ['EMP1006', 'Anna Bell', 'anna.bell@example.com', 'Sales', '35000', '2023-02-15'],          # Salary too low
        ['EMP1007', 'Mike Ross', 'mike.ross@example.com', 'Engineering', '95000', '2023/04/30'],       # Invalid date format
    ]
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def define_schema():
    """Defines the validation schema using Cerberus syntax."""
    schema = {
        'employee_id': {'type': 'string', 'regex': r'^EMP\d{4}$'},
        'name': {'type': 'string', 'required': True, 'empty': False},
        'email': {'type': 'string', 'regex': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'},
        'department': {'type': 'string', 'allowed': ['Engineering', 'Marketing', 'Sales', 'Finance']},
        'salary': {'type': 'integer', 'min': 40000, 'coerce': int},
        'hire_date': {'type': 'datetime', 'coerce': pd.to_datetime, 'datetime_format': '%Y-%m-%d'}
    }
    return schema

def validate_csv(file_path, schema):
    """Validates a CSV file against a Cerberus schema and returns invalid rows."""
    print(f"\nReading and validating {file_path}...")
    df = pd.read_csv(file_path)
    validator = Validator(schema)
    invalid_rows = []

    for index, row in df.iterrows():
        row_data = row.to_dict()
        if not validator.validate(row_data):
            invalid_rows.append({
                'row_number': index + 2, # +2 to account for header and 0-based index
                'data': row_data,
                'errors': validator.errors
            })
    return invalid_rows, len(df)

def generate_report(file_path, invalid_rows, total_rows):
    """Generates a detailed validation report as a text file."""
    print(f"Generating validation report: {REPORT_FILE}")
    valid_rows = total_rows - len(invalid_rows)

    with open(REPORT_FILE, 'w') as f:
        f.write("---" + " CSV Validation Report ---" + "\n\n")
        f.write(f"Source File: {file_path}\n")
        f.write(f"Validation Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n--- Summary ---" + "\n")
        f.write(f"Total Rows Processed: {total_rows}\n")
        f.write(f"Valid Rows: {valid_rows} ({valid_rows/total_rows:.2%})\n")
        f.write(f"Invalid Rows: {len(invalid_rows)} ({len(invalid_rows)/total_rows:.2%})\n")
        f.write("\n--- Detailed Error Report ---" + "\n")

        if not invalid_rows:
            f.write("No errors found. The file is valid.\n")
        else:
            for error_info in invalid_rows:
                f.write(f"\n- Row {error_info['row_number']}:\n")
                f.write(f"  Data: {error_info['data']}\n")
                f.write(f"  Errors:\n")
                for field, messages in error_info['errors'].items():
                    f.write(f"    - Field '{field}': {messages[0]}\n")
    print("Report generation complete.")

if __name__ == "__main__":
    print("--- Starting Data Validation Script ---")
    generate_sample_csv()
    validation_schema = define_schema()
    invalid_data, total = validate_csv(CSV_FILE, validation_schema)
    generate_report(CSV_FILE, invalid_data, total)
    print(f"\n--- Process Finished. Check '{REPORT_FILE}' for details. ---")
