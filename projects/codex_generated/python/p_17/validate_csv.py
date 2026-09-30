#!/usr/bin/env python3
"""Validate CSV rows against a JSON Schema and report issues."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
from jsonschema import Draft202012Validator, FormatChecker, ValidationError


@dataclass
class RowValidationResult:
    index: int
    errors: List[str]
    data: Dict[str, object]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate CSV data against a JSON schema")
    parser.add_argument("--csv", required=True, help="Path to the CSV file to validate")
    parser.add_argument("--schema", required=True, help="Path to the JSON schema file")
    parser.add_argument(
        "--report",
        default="validation_report.json",
        help="Path to write the validation summary report (JSON)",
    )
    parser.add_argument(
        "--invalid-csv",
        default="invalid_rows.csv",
        help="Path to write rows that failed validation",
    )
    parser.add_argument("--encoding", default="utf-8", help="CSV encoding (default: utf-8)")
    parser.add_argument(
        "--index-column",
        default=None,
        help="Optional column to treat as identifier instead of row number",
    )
    return parser.parse_args()


def load_schema(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON schema file: {exc}") from exc


def load_dataframe(path: Path, encoding: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    try:
        return pd.read_csv(path, encoding=encoding)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"Failed to read CSV file: {exc}") from exc


def format_error(error: ValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "<row>"
    return f"{location}: {error.message}"


def normalize_row(row: pd.Series) -> Dict[str, object]:
    normalized = row.where(pd.notna(row), None)
    return normalized.to_dict()


def validate_rows(
    df: pd.DataFrame,
    validator: Draft202012Validator,
    index_column: Optional[str] = None,
) -> List[RowValidationResult]:
    invalid_rows: List[RowValidationResult] = []
    for idx, row in df.iterrows():
        data = normalize_row(row)
        row_id = data.get(index_column) if index_column and index_column in data else idx + 1
        errors = [format_error(err) for err in validator.iter_errors(data)]
        if errors:
            invalid_rows.append(RowValidationResult(index=row_id, errors=errors, data=data))
    return invalid_rows


def summarize_results(
    total_rows: int,
    invalid_results: List[RowValidationResult],
) -> Dict[str, object]:
    error_counter = Counter()
    for result in invalid_results:
        error_counter.update(result.errors)

    summary = {
        "total_rows": total_rows,
        "valid_rows": total_rows - len(invalid_results),
        "invalid_rows": len(invalid_results),
        "error_details": [
            {"message": message, "count": count}
            for message, count in error_counter.most_common()
        ],
        "invalid_row_examples": [
            {"row_identifier": result.index, "errors": result.errors}
            for result in invalid_results[:10]
        ],
    }
    return summary


def write_invalid_rows(path: Path, invalid_results: Iterable[RowValidationResult]) -> None:
    rows = []
    for result in invalid_results:
        row_copy = dict(result.data)
        row_copy["__validation_errors"] = " | ".join(result.errors)
        row_copy["__row_identifier"] = result.index
        rows.append(row_copy)
    if rows:
        df = pd.DataFrame(rows)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Invalid rows written to {path}")
    else:
        print("No invalid rows detected.")


def write_report(path: Path, report: Dict[str, object], invalid_results: List[RowValidationResult]) -> None:
    report_payload = dict(report)
    report_payload["invalid_rows"] = [
        {
            "row_identifier": result.index,
            "errors": result.errors,
            "data": result.data,
        }
        for result in invalid_results
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print(f"Validation report saved to {path}")


def main() -> None:
    args = parse_args()
    try:
        schema = load_schema(Path(args.schema))
        df = load_dataframe(Path(args.csv), args.encoding)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    invalid_rows = validate_rows(df, validator, args.index_column)
    summary = summarize_results(len(df), invalid_rows)

    write_invalid_rows(Path(args.invalid_csv), invalid_rows)
    write_report(Path(args.report), summary, invalid_rows)

    total = summary["total_rows"]
    print(
        f"Validation complete. Total rows: {total}, valid: {summary['valid_rows']}, invalid: {summary['invalid_rows']}"
    )


if __name__ == "__main__":
    main()
