#!/usr/bin/env python3
"""Extract text from PDFs, compute word statistics, and export structured results."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pdfplumber

WORD_RE = re.compile(r"[A-Za-z']+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF text extraction and analysis tool")
    parser.add_argument("--input", required=True, help="Path to a PDF file or directory containing PDFs")
    parser.add_argument(
        "--output",
        default="analysis.json",
        help="Path to the output file (JSON or CSV based on extension)",
    )
    parser.add_argument(
        "--limit-pages",
        type=int,
        default=None,
        help="Optional limit on pages processed per PDF",
    )
    return parser.parse_args()


def collect_pdf_paths(input_path: Path) -> List[Path]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input path not found: {input_path}")

    if input_path.is_file():
        if input_path.suffix.lower() != ".pdf":
            raise ValueError(f"Input file is not a PDF: {input_path}")
        return [input_path]

    pdf_paths = sorted(p for p in input_path.rglob("*.pdf"))
    if not pdf_paths:
        raise ValueError(f"No PDF files found in directory: {input_path}")
    return pdf_paths


def extract_text_from_pdf(pdf_path: Path, limit_pages: int | None) -> str:
    text_chunks: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            if limit_pages is not None and page_number > limit_pages:
                break
            page_text = page.extract_text() or ""
            text_chunks.append(page_text)
    return "\n".join(text_chunks)


def tokenize(text: str) -> Iterable[str]:
    for match in WORD_RE.finditer(text.lower()):
        yield match.group()


def analyze_text(text: str) -> Dict[str, object]:
    words = list(tokenize(text))
    counter = Counter(words)
    total_words = sum(counter.values())
    unique_words = len(counter)
    top_words = counter.most_common(20)
    return {
        "word_count": total_words,
        "unique_words": unique_words,
        "top_words": top_words,
    }


def analyze_pdfs(pdf_paths: Iterable[Path], limit_pages: int | None) -> Dict[str, Dict[str, object]]:
    results: Dict[str, Dict[str, object]] = {}
    for pdf_path in pdf_paths:
        text = extract_text_from_pdf(pdf_path, limit_pages)
        analysis = analyze_text(text)
        analysis["characters"] = len(text)
        analysis["file"] = str(pdf_path.resolve())
        results[str(pdf_path.name)] = analysis
    return results


def save_json(results: Dict[str, Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)


def save_csv(results: Dict[str, Dict[str, object]], output_path: Path) -> None:
    import csv

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["file", "word_count", "unique_words", "characters", "top_words"]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for analysis in results.values():
            row = {
                "file": analysis["file"],
                "word_count": analysis["word_count"],
                "unique_words": analysis["unique_words"],
                "characters": analysis["characters"],
                "top_words": "; ".join(f"{word}:{count}" for word, count in analysis["top_words"]),
            }
            writer.writerow(row)


def save_results(results: Dict[str, Dict[str, object]], output_path: Path) -> None:
    suffix = output_path.suffix.lower()
    if suffix == ".json":
        save_json(results, output_path)
    elif suffix == ".csv":
        save_csv(results, output_path)
    else:
        raise ValueError("Unsupported output extension. Use .json or .csv")


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    pdf_paths = collect_pdf_paths(input_path)
    results = analyze_pdfs(pdf_paths, args.limit_pages)
    save_results(results, output_path)

    print(f"Processed {len(pdf_paths)} PDF(s).")
    print(f"Results saved to {output_path.resolve()}")


if __name__ == "__main__":
    main()
