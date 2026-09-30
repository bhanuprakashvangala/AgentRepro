"""
JSON to CSV Converter with Nested Object Flattening
Handles deeply nested JSON structures and arrays
"""

import pandas as pd
import json
from typing import Any, Dict, List, Union
from pathlib import Path


def flatten_json(
    nested_json: Dict[str, Any],
    parent_key: str = '',
    sep: str = '_'
) -> Dict[str, Any]:
    """
    Recursively flatten a nested JSON object.

    Args:
        nested_json: The nested JSON object to flatten
        parent_key: The parent key for nested elements
        sep: Separator between parent and child keys

    Returns:
        Flattened dictionary
    """
    items = []

    for key, value in nested_json.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            # Recursively flatten nested dictionaries
            items.extend(flatten_json(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            # Handle arrays
            if len(value) == 0:
                items.append((new_key, None))
            elif isinstance(value[0], dict):
                # Array of objects - create separate columns for each index
                for i, item in enumerate(value):
                    items.extend(
                        flatten_json(item, f"{new_key}_{i}", sep=sep).items()
                    )
            else:
                # Array of primitives - join as string
                items.append((new_key, json.dumps(value)))
        else:
            # Primitive value
            items.append((new_key, value))

    return dict(items)


def json_to_csv(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    sep: str = '_',
    encoding: str = 'utf-8'
) -> None:
    """
    Convert JSON file to CSV with nested object flattening.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output CSV file
        sep: Separator for flattened keys
        encoding: File encoding
    """
    # Read JSON file
    with open(input_file, 'r', encoding=encoding) as f:
        data = json.load(f)

    # Handle both single object and array of objects
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise ValueError("JSON must be an object or array of objects")

    # Flatten each record
    flattened_data = [flatten_json(record, sep=sep) for record in data]

    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)

    # Write to CSV
    df.to_csv(output_file, index=False, encoding=encoding)

    print(f"✓ Converted {len(df)} records from JSON to CSV")
    print(f"✓ Output file: {output_file}")
    print(f"✓ Columns created: {len(df.columns)}")


def json_string_to_csv(
    json_string: str,
    output_file: Union[str, Path],
    sep: str = '_',
    encoding: str = 'utf-8'
) -> None:
    """
    Convert JSON string to CSV with nested object flattening.

    Args:
        json_string: JSON string to convert
        output_file: Path to output CSV file
        sep: Separator for flattened keys
        encoding: File encoding
    """
    # Parse JSON string
    data = json.loads(json_string)

    # Handle both single object and array of objects
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise ValueError("JSON must be an object or array of objects")

    # Flatten each record
    flattened_data = [flatten_json(record, sep=sep) for record in data]

    # Convert to DataFrame
    df = pd.DataFrame(flattened_data)

    # Write to CSV
    df.to_csv(output_file, index=False, encoding=encoding)

    print(f"✓ Converted {len(df)} records from JSON to CSV")
    print(f"✓ Output file: {output_file}")
    print(f"✓ Columns created: {len(df.columns)}")


def main():
    """Example usage demonstrating the converter."""

    # Example 1: Complex nested JSON
    sample_data = [
        {
            "id": 1,
            "name": "John Doe",
            "contact": {
                "email": "john@example.com",
                "phone": {
                    "mobile": "555-1234",
                    "home": "555-5678"
                }
            },
            "orders": [
                {"product": "Laptop", "price": 999.99},
                {"product": "Mouse", "price": 29.99}
            ],
            "tags": ["premium", "tech"]
        },
        {
            "id": 2,
            "name": "Jane Smith",
            "contact": {
                "email": "jane@example.com",
                "phone": {
                    "mobile": "555-9012",
                    "home": "555-3456"
                }
            },
            "orders": [
                {"product": "Keyboard", "price": 79.99}
            ],
            "tags": ["standard"]
        }
    ]

    # Save sample JSON
    with open('sample_input.json', 'w') as f:
        json.dump(sample_data, f, indent=2)

    print("=" * 60)
    print("JSON to CSV Converter - Example Usage")
    print("=" * 60)

    # Convert JSON file to CSV
    json_to_csv('sample_input.json', 'output.csv')

    print("\n" + "=" * 60)
    print("Sample of flattened structure:")
    print("=" * 60)
    df = pd.read_csv('output.csv')
    print(df.to_string(max_colwidth=30))

    print("\n" + "=" * 60)
    print("Column names:")
    print("=" * 60)
    for col in df.columns:
        print(f"  - {col}")


if __name__ == "__main__":
    main()
