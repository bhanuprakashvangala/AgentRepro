#!/usr/bin/env python3
"""Convert nested JSON documents into flattened CSV using pandas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Flatten JSON into normalized CSV")
    parser.add_argument("--input", required=True, help="Path to JSON file (object or array)")
    parser.add_argument("--output", required=True, help="Destination CSV path")
    parser.add_argument(
        "--orient",
        choices=["records", "list"],
        default="records",
        help="Input orientation: 'records' expects list at root (default), 'list' flattens nested list under a key",
    )
    parser.add_argument(
        "--root-key",
        help="When using --orient=list, provide JSON key containing the records list",
    )
    parser.add_argument(
        "--sep",
        default=".",
        help="Separator for flattened column names (default '.')",
    )
    parser.add_argument(
        "--explode",
        nargs="*",
        help="Optional list of column names to explode (arrays -> separate rows)",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload


def extract_records(payload: Any, orient: str, root_key: str | None) -> List[Dict[str, Any]]:
    if orient == "records":
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return [payload]
        raise ValueError("For orient=records, JSON must be an array or object")
    if not isinstance(payload, dict):
        raise ValueError("For orient=list, JSON must be an object containing the records list")
    if not root_key:
        raise ValueError("--root-key must be specified when orient=list")
    records = payload.get(root_key)
    if not isinstance(records, list):
        raise ValueError(f"Expected list under key '{root_key}'")
    return records


def flatten_records(records: Iterable[Dict[str, Any]], sep: str) -> pd.DataFrame:
    normalized = pd.json_normalize(records, sep=sep)
    return normalized


def explode_columns(df: pd.DataFrame, columns: List[str] | None) -> pd.DataFrame:
    if not columns:
        return df
    for column in columns:
        if column in df.columns:
            df = df.explode(column, ignore_index=True)
    return df


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    payload = load_json(input_path)
    records = extract_records(payload, args.orient, args.root_key)
    df = flatten_records(records, args.sep)
    df = explode_columns(df, args.explode)

    df.to_csv(output_path, index=False)
    print(f"CSV written to {output_path}")


if __name__ == "__main__":
    main()
