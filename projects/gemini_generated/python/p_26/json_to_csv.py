import pandas as pd
import json
import argparse
import os

DEFAULT_INPUT = "sample.json"
DEFAULT_OUTPUT = "output.csv"

def generate_sample_json(filename=DEFAULT_INPUT):
    """Generates a sample JSON file with nested objects and arrays."""
    if os.path.exists(filename):
        print(f"Sample JSON '{filename}' already exists.")
        return

    print(f"Generating sample JSON file: {filename}")
    data = [
        {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "address": {
                "street": "123 Main St",
                "city": "Anytown"
            },
            "orders": [
                {"order_id": "A101", "amount": 150.75, "date": "2023-01-15"},
                {"order_id": "A102", "amount": 200.00, "date": "2023-02-20"}
            ]
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "address": {
                "street": "456 Oak Ave",
                "city": "Someville"
            },
            "orders": [
                {"order_id": "B201", "amount": 300.50, "date": "2023-03-10"}
            ]
        },
        {
            "id": 3,
            "name": "Chris Lee",
            "email": "chris.lee@example.com",
            "address": {
                "street": "789 Pine Ln",
                "city": "Otherplace"
            },
            "orders": [] # User with no orders
        }
    ]
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def convert_json_to_csv(input_path, output_path):
    """Converts a nested JSON file to a flattened CSV file."""
    print(f"\nConverting '{input_path}' to '{output_path}'...")
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_path}'. Please check the file format.")
        return

    # --- The core of the flattening logic ---
    # `record_path` specifies the list to unpack into rows.
    # `meta` specifies the parent-level fields to repeat for each unpacked item.
    # `meta_prefix` and `record_prefix` can be used to avoid column name collisions.
    # Nested objects like 'address' are specified with a list path.
    df = pd.json_normalize(
        data,
        record_path=['orders'],
        meta=[
            'id',
            'name',
            'email',
            ['address', 'street'],
            ['address', 'city']
        ],
        errors='ignore' # Ignores records that don't have the 'orders' path (e.g., users with no orders)
    )

    # Rename the flattened address columns for clarity
    df.rename(columns={'address.street': 'address_street', 'address.city': 'address_city'}, inplace=True)

    # Save the flattened DataFrame to CSV
    df.to_csv(output_path, index=False)
    print(f"Successfully created flattened CSV: {output_path}")
    print("\n--- CSV Preview ---")
    print(df.head().to_string())
    print("-------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a nested JSON file to a flat CSV.")
    parser.add_argument("-i", "--input", help=f"Input JSON file path (default: {DEFAULT_INPUT}).")
    parser.add_argument("-o", "--output", help=f"Output CSV file path (default: {DEFAULT_OUTPUT}).")
    parser.add_argument("--demo", action="store_true", help="Run a self-contained demo with sample data.")
    args = parser.parse_args()

    if args.demo:
        generate_sample_json(DEFAULT_INPUT)
        convert_json_to_csv(DEFAULT_INPUT, DEFAULT_OUTPUT)
    elif args.input and args.output:
        convert_json_to_csv(args.input, args.output)
    else:
        print("Please provide input and output files, or use the --demo flag.")
        parser.print_help()
