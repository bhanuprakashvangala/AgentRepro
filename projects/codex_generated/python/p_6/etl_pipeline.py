#!/usr/bin/env python3
"""Simple ETL pipeline: extract CSV, transform with pandas, and load into SQLite via SQLAlchemy."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a CSV -> SQLite ETL pipeline with summary report")
    parser.add_argument("--input", required=True, help="Path to the input CSV file")
    parser.add_argument("--database", default="etl_output.db", help="SQLite database file to create or update")
    parser.add_argument("--table", default="records", help="Destination table name inside SQLite")
    parser.add_argument(
        "--summary",
        default="summary.json",
        help="Path to write the summary statistics report (JSON)",
    )
    parser.add_argument(
        "--if-exists",
        choices=["fail", "replace", "append"],
        default="replace",
        help="Behavior when the target table already exists (default: replace)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSV file encoding (default: utf-8)",
    )
    return parser.parse_args()


def extract_csv(path: Path, encoding: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")
    try:
        df = pd.read_csv(path, encoding=encoding)
    except Exception as exc:  # pylint: disable=broad-except
        raise ValueError(f"Unable to read CSV file: {path} ({exc})") from exc
    if df.empty:
        raise ValueError("Input CSV contains no rows")
    return df


def transform_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    transformed = df.copy()
    transformed = transformed.drop_duplicates()

    numeric_cols = transformed.select_dtypes(include=["number"]).columns
    categorical_cols = transformed.select_dtypes(include=["object", "category"]).columns
    datetime_cols = transformed.select_dtypes(include=["datetime", "datetimetz"]).columns

    # Attempt to convert obvious datetime columns automatically
    for col in transformed.columns:
        if col in datetime_cols:
            continue
        if transformed[col].dtype == "object":
            try:
                transformed[col] = pd.to_datetime(transformed[col])
            except (ValueError, TypeError):
                pass

    # Recompute dtypes after conversions
    numeric_cols = transformed.select_dtypes(include=["number"]).columns
    categorical_cols = transformed.select_dtypes(include=["object", "category"]).columns
    datetime_cols = transformed.select_dtypes(include=["datetime", "datetimetz"]).columns

    # Handle missing values
    for col in numeric_cols:
        median_value = transformed[col].median()
        transformed[col] = transformed[col].fillna(median_value)

    for col in categorical_cols:
        transformed[col] = transformed[col].fillna("Unknown")

    for col in datetime_cols:
        transformed[col] = transformed[col].fillna(pd.Timestamp("1970-01-01"))

    summary = generate_summary(transformed)

    return transformed, summary


def generate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}

    numeric_desc = df.select_dtypes(include=["number"]).describe().transpose()
    numeric_summary: Dict[str, Dict[str, Any]] = {}
    for column, stats in numeric_desc.to_dict(orient="index").items():
        numeric_summary[column] = {
            metric: None if pd.isna(value) else float(value) for metric, value in stats.items()
        }
    summary["numeric"] = numeric_summary

    categorical_info: Dict[str, Dict[str, Any]] = {}
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        value_counts = df[col].value_counts(dropna=False).head(5)
        categorical_info[col] = {
            str(category) if not pd.isna(category) else "NaN": int(count)
            for category, count in value_counts.items()
        }
    summary["categorical"] = categorical_info

    return summary


def load_to_sqlite(df: pd.DataFrame, engine: Engine | Connection, table_name: str, if_exists: str) -> None:
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)


def write_summary(summary: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, indent=2, default=str)


def get_engine(database_path: Path) -> Engine:
    return create_engine(f"sqlite:///{database_path}")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    database_path = Path(args.database)
    summary_path = Path(args.summary)

    try:
        df = extract_csv(input_path, args.encoding)
        transformed_df, summary = transform_dataframe(df)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error during extraction/transformation: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        engine = get_engine(database_path)
        with engine.begin() as connection:
            load_to_sqlite(transformed_df, connection, args.table, args.if_exists)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error during load to SQLite: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        write_summary(summary, summary_path)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to write summary report: {exc}", file=sys.stderr)
        sys.exit(1)

    print("ETL completed successfully.")
    print(f"Rows loaded: {len(transformed_df)}")
    print(f"SQLite database: {database_path}")
    print(f"Table name: {args.table}")
    print(f"Summary report: {summary_path}")


if __name__ == "__main__":
    main()
