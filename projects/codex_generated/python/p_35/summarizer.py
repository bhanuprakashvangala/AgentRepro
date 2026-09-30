#!/usr/bin/env python3
"""Text summarization CLI supporting batch processing and configurable length."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from transformers import pipeline

DEFAULT_MODEL = "facebook/bart-large-cnn"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize text documents using transformer models")
    parser.add_argument("--input", nargs="+", required=True, help="Text files to summarize")
    parser.add_argument("--output-dir", required=True, help="Directory to write summary files")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Hugging Face model for summarization")
    parser.add_argument("--min-length", type=int, default=50, help="Minimum summary length")
    parser.add_argument("--max-length", type=int, default=150, help="Maximum summary length")
    parser.add_argument(
        "--batch-size", type=int, default=4, help="Number of documents to summarize per batch"
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Device to run model on (e.g., cpu, cuda:0)",
    )
    return parser.parse_args()


def read_documents(files: Iterable[str]) -> List[str]:
    documents = []
    for path_str in files:
        path = Path(path_str)
        if not path.exists():
            print(f"Warning: file not found {path}")
            continue
        documents.append(path.read_text(encoding="utf-8", errors="ignore"))
    return documents


def summarize_texts(texts: List[str], summarizer_pipeline, min_length: int, max_length: int, batch_size: int) -> List[str]:
    summaries = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        outputs = summarizer_pipeline(batch, min_length=min_length, max_length=max_length, truncation=True)
        for output in outputs:
            summaries.append(output["summary_text"])
    return summaries


def main() -> None:
    args = parse_args()
    texts = read_documents(args.input)
    if not texts:
        print("No documents to summarize.")
        return

    device = 0 if args.device.startswith("cuda") else -1
    summarizer_pipeline = pipeline(
        "summarization",
        model=args.model,
        tokenizer=args.model,
        device=device,
    )

    summaries = summarize_texts(texts, summarizer_pipeline, args.min_length, args.max_length, args.batch_size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for path_str, summary in zip(args.input, summaries):
        original_path = Path(path_str)
        output_path = output_dir / (original_path.stem + "_summary.txt")
        output_path.write_text(summary, encoding="utf-8")
        print(f"Summary written to {output_path}")


if __name__ == "__main__":
    main()
