#!/usr/bin/env python3
"""Batch sentiment analysis for customer reviews using TextBlob."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List

from textblob import TextBlob


@dataclass
class SentimentResult:
    """Container for per-review sentiment output."""

    original_text: str
    label: str
    polarity: float
    subjectivity: float
    confidence: float

    def to_serializable(self) -> Dict[str, object]:
        data = asdict(self)
        data["confidence"] = round(self.confidence, 4)
        data["polarity"] = round(self.polarity, 4)
        data["subjectivity"] = round(self.subjectivity, 4)
        return data


def classify_sentiment(polarity: float, threshold: float) -> str:
    if polarity >= threshold:
        return "positive"
    if polarity <= -threshold:
        return "negative"
    return "neutral"


def confidence_from_polarity(polarity: float, label: str) -> float:
    if label == "neutral":
        return max(0.0, 1.0 - abs(polarity))
    return min(1.0, max(0.0, abs(polarity)))


def analyze_text(text: str, threshold: float) -> SentimentResult:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    label = classify_sentiment(polarity, threshold)
    confidence = confidence_from_polarity(polarity, label)
    return SentimentResult(
        original_text=text,
        label=label,
        polarity=polarity,
        subjectivity=subjectivity,
        confidence=confidence,
    )


def analyze_reviews(rows: Iterable[Dict[str, str]], text_column: str, threshold: float) -> List[SentimentResult]:
    results: List[SentimentResult] = []
    for index, row in enumerate(rows, start=1):
        text = (row.get(text_column) or "").strip()
        if not text:
            print(f"Row {index}: empty text skipped", file=sys.stderr)
            continue
        results.append(analyze_text(text, threshold))
    return results


def generate_report(results: List[SentimentResult]) -> Dict[str, object]:
    total = len(results)
    distribution = Counter(result.label for result in results)

    def safe_average(values: Iterable[float]) -> float:
        values = list(values)
        if not values:
            return 0.0
        return sum(values) / len(values)

    report = {
        "total_reviews": total,
        "label_distribution": dict(distribution),
        "average_polarity": round(safe_average(result.polarity for result in results), 4),
        "average_subjectivity": round(safe_average(result.subjectivity for result in results), 4),
        "average_confidence": round(safe_average(result.confidence for result in results), 4),
    }

    for label in ("positive", "neutral", "negative"):
        subset = [result.confidence for result in results if result.label == label]
        report[f"average_confidence_{label}"] = round(safe_average(subset), 4)

    return report


def save_results_csv(results: List[SentimentResult], output_path: Path) -> None:
    fieldnames = ["text", "label", "polarity", "subjectivity", "confidence"]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            row = {
                "text": result.original_text,
                "label": result.label,
                "polarity": round(result.polarity, 4),
                "subjectivity": round(result.subjectivity, 4),
                "confidence": round(result.confidence, 4),
            }
            writer.writerow(row)


def save_report(report: Dict[str, object], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as report_file:
        json.dump(report, report_file, indent=2)


def load_reviews(input_path: Path, text_column: str, encoding: str) -> List[Dict[str, str]]:
    try:
        with input_path.open("r", newline="", encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("Input CSV appears to be empty or missing a header row.")
            if text_column not in fieldnames:
                raise ValueError(
                    f"Column '{text_column}' not found in CSV header: {fieldnames}"
                )
            return list(reader)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Input file not found: {input_path}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify customer reviews as positive, negative, or neutral using TextBlob."
    )
    parser.add_argument("--input", required=True, help="Path to CSV file containing reviews.")
    parser.add_argument(
        "--text-column",
        default="review",
        help="Name of the column containing review text (default: review)",
    )
    parser.add_argument(
        "--output",
        default="sentiment_results.csv",
        help="Path for the annotated sentiment CSV output.",
    )
    parser.add_argument(
        "--report",
        default="sentiment_report.json",
        help="Path for the summary sentiment report in JSON format.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="Minimum polarity magnitude for positive/negative classification (default: 0.1).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding of the input CSV file (default: utf-8).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        input_path = Path(args.input)
        output_path = Path(args.output)
        report_path = Path(args.report)

        rows = load_reviews(input_path, args.text_column, args.encoding)
        results = analyze_reviews(rows, args.text_column, args.threshold)

        if not results:
            print("No reviews with content were found. Nothing to analyze.", file=sys.stderr)
            sys.exit(1)

        save_results_csv(results, output_path)
        report = generate_report(results)
        save_report(report, report_path)

        print(f"Analyzed {len(results)} reviews.")
        print(json.dumps(report, indent=2))

    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
