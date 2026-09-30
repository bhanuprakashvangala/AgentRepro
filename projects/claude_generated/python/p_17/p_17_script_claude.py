"""
CSV Data Validation Script
Validates CSV files against defined schemas using pandas and cerberus.
"""

import sys
import pandas as pd
from cerberus import Validator
from datetime import datetime
from typing import Dict, List, Any
import json


class CSVValidator:
    """Validates CSV files against defined schemas."""

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize the validator with a schema.

        Args:
            schema: Cerberus schema dictionary defining validation rules
        """
        self.schema = schema
        self.validator = Validator(schema)
        self.validation_results = []

    def validate_csv(self, csv_file: str, delimiter: str = ',') -> pd.DataFrame:
        """
        Validate a CSV file against the schema.

        Args:
            csv_file: Path to CSV file
            delimiter: CSV delimiter character

        Returns:
            DataFrame with validation results
        """
        print(f"Loading CSV file: {csv_file}")

        # Load CSV
        try:
            df = pd.read_csv(csv_file, delimiter=delimiter)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            sys.exit(1)

        print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

        # Validate each row
        self.validation_results = []

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            is_valid = self.validator.validate(row_dict)

            result = {
                'row_number': idx + 2,  # +2 because CSV is 1-indexed and has header
                'is_valid': is_valid,
                'errors': self.validator.errors.copy() if not is_valid else {},
                'data': row_dict
            }

            self.validation_results.append(result)

        return self._create_results_dataframe()

    def _create_results_dataframe(self) -> pd.DataFrame:
        """Create a DataFrame from validation results."""
        results = []

        for result in self.validation_results:
            row_data = {
                'Row': result['row_number'],
                'Valid': result['is_valid'],
                'Error_Count': len(result['errors']),
                'Errors': self._format_errors(result['errors'])
            }

            # Add original data columns
            for key, value in result['data'].items():
                row_data[f'Data_{key}'] = value

            results.append(row_data)

        return pd.DataFrame(results)

    def _format_errors(self, errors: Dict) -> str:
        """Format error dictionary into readable string."""
        if not errors:
            return ""

        error_messages = []
        for field, error_list in errors.items():
            error_messages.append(f"{field}: {', '.join(error_list)}")

        return " | ".join(error_messages)

    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a detailed validation report.

        Args:
            output_file: Optional file path to save report

        Returns:
            Report as string
        """
        if not self.validation_results:
            return "No validation results available. Run validate_csv() first."

        total_rows = len(self.validation_results)
        valid_rows = sum(1 for r in self.validation_results if r['is_valid'])
        invalid_rows = total_rows - valid_rows

        # Generate report
        report_lines = [
            "=" * 80,
            "CSV VALIDATION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY",
            "-" * 80,
            f"Total Rows Processed: {total_rows}",
            f"Valid Rows: {valid_rows} ({valid_rows/total_rows*100:.2f}%)",
            f"Invalid Rows: {invalid_rows} ({invalid_rows/total_rows*100:.2f}%)",
            "",
        ]

        if invalid_rows > 0:
            report_lines.extend([
                "INVALID ROWS DETAIL",
                "-" * 80,
            ])

            for result in self.validation_results:
                if not result['is_valid']:
                    report_lines.append(f"\nRow {result['row_number']}:")
                    report_lines.append(f"  Data: {json.dumps(result['data'], indent=8)}")
                    report_lines.append(f"  Errors:")

                    for field, errors in result['errors'].items():
                        for error in errors:
                            report_lines.append(f"    - {field}: {error}")

        # Error frequency analysis
        error_frequency = {}
        for result in self.validation_results:
            if not result['is_valid']:
                for field, errors in result['errors'].items():
                    for error in errors:
                        key = f"{field}: {error}"
                        error_frequency[key] = error_frequency.get(key, 0) + 1

        if error_frequency:
            report_lines.extend([
                "",
                "ERROR FREQUENCY ANALYSIS",
                "-" * 80,
            ])

            for error, count in sorted(error_frequency.items(),
                                      key=lambda x: x[1],
                                      reverse=True):
                report_lines.append(f"{count:4d}x  {error}")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {output_file}")

        return report


# Example schema definitions
EXAMPLE_SCHEMAS = {
    "users": {
        "user_id": {
            "type": "integer",
            "required": True,
            "min": 1
        },
        "username": {
            "type": "string",
            "required": True,
            "minlength": 3,
            "maxlength": 50,
            "regex": "^[a-zA-Z0-9_]+$"
        },
        "email": {
            "type": "string",
            "required": True,
            "regex": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        },
        "age": {
            "type": "integer",
            "required": True,
            "min": 18,
            "max": 120
        },
        "balance": {
            "type": "float",
            "required": True,
            "min": 0.0
        },
        "status": {
            "type": "string",
            "required": True,
            "allowed": ["active", "inactive", "suspended"]
        }
    },

    "products": {
        "product_id": {
            "type": "string",
            "required": True,
            "regex": "^PRD-[0-9]{6}$"
        },
        "name": {
            "type": "string",
            "required": True,
            "minlength": 1,
            "maxlength": 200
        },
        "price": {
            "type": "float",
            "required": True,
            "min": 0.01
        },
        "quantity": {
            "type": "integer",
            "required": True,
            "min": 0
        },
        "category": {
            "type": "string",
            "required": True,
            "allowed": ["electronics", "clothing", "food", "books", "other"]
        }
    }
}


def main():
    """Main execution function with example usage."""

    print("CSV Data Validation Script")
    print("=" * 80)

    # Example 1: Validate users CSV
    print("\n1. Creating sample users CSV...")

    sample_users = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5, 6],
        'username': ['john_doe', 'ab', 'jane_smith', 'bob123', 'alice_wonder', 'charlie@invalid'],
        'email': ['john@example.com', 'alice@test.com', 'invalid-email',
                  'jane@example.com', 'alice@example.com', 'charlie@test.com'],
        'age': [25, 30, 17, 45, 150, 28],
        'balance': [100.50, -50.0, 200.0, 75.25, 300.0, 50.0],
        'status': ['active', 'inactive', 'active', 'invalid_status', 'suspended', 'active']
    })

    sample_users.to_csv('sample_users.csv', index=False)
    print("Created: sample_users.csv")

    # Validate users CSV
    print("\n2. Validating users CSV against schema...")
    validator = CSVValidator(EXAMPLE_SCHEMAS['users'])
    results_df = validator.validate_csv('sample_users.csv')

    # Save results
    results_df.to_csv('validation_results.csv', index=False)
    print("\nValidation results saved to: validation_results.csv")

    # Generate and display report
    print("\n3. Generating validation report...")
    report = validator.generate_report('validation_report.txt')
    print("\n" + report)

    # Example 2: Validate products CSV
    print("\n\n4. Creating sample products CSV...")

    sample_products = pd.DataFrame({
        'product_id': ['PRD-000001', 'PRD-000002', 'INVALID', 'PRD-000004'],
        'name': ['Laptop', 'Mouse', 'Keyboard', 'M'],
        'price': [999.99, 25.50, -10.0, 45.00],
        'quantity': [10, 50, 100, -5],
        'category': ['electronics', 'electronics', 'invalid_category', 'electronics']
    })

    sample_products.to_csv('sample_products.csv', index=False)
    print("Created: sample_products.csv")

    print("\n5. Validating products CSV against schema...")
    validator2 = CSVValidator(EXAMPLE_SCHEMAS['products'])
    results_df2 = validator2.validate_csv('sample_products.csv')

    results_df2.to_csv('validation_results_products.csv', index=False)
    report2 = validator2.generate_report('validation_report_products.txt')
    print("\n" + report2)

    print("\n" + "=" * 80)
    print("Validation complete!")
    print("\nFiles created:")
    print("  - sample_users.csv (sample data)")
    print("  - validation_results.csv (detailed results)")
    print("  - validation_report.txt (human-readable report)")
    print("  - sample_products.csv (sample data)")
    print("  - validation_results_products.csv (detailed results)")
    print("  - validation_report_products.txt (human-readable report)")


if __name__ == "__main__":
    main()
