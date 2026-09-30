#!/usr/bin/env python3
"""Plagiarism detection tool using difflib for similarity scoring and highlighting."""

from __future__ import annotations

import argparse
import difflib
import itertools
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from difflib import SequenceMatcher


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect similarity between text documents")
    parser.add_argument("--inputs", nargs="+", required=True, help="Text files to compare")
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to write similarity reports",
    )
    parser.add_argument(
        "--min-match-length",
        type=int,
        default=30,
        help="Minimum number of matching characters to highlight (default: 30)",
    )
    return parser.parse_args()


def load_documents(paths: Iterable[str]) -> Dict[str, str]:
    contents: Dict[str, str] = {}
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            print(f"Warning: file not found {path}")
            continue
        contents[path.name] = path.read_text(encoding="utf-8", errors="ignore")
    return contents


def compute_similarity(text_a: str, text_b: str) -> float:
    matcher = SequenceMatcher(None, text_a, text_b, autojunk=False)
    return matcher.ratio() * 100


def find_matching_blocks(text_a: str, text_b: str, min_length: int) -> List[Tuple[int, int, int]]:
    matcher = SequenceMatcher(None, text_a, text_b, autojunk=False)
    blocks = matcher.get_matching_blocks()
    return [block for block in blocks if block.size >= min_length]


def highlight_matches(text: str, matches: List[Tuple[int, int, int]], highlight_map: Dict[int, Tuple[int, int]]) -> str:
    # highlights stored as start/end positions for <mark> tags
    result = []
    last_index = 0
    sorted_matches = sorted(highlight_map.items(), key=lambda item: item[0])
    for start, (end, _) in sorted_matches:
        result.append(text[last_index:start])
        result.append("<mark>")
        result.append(text[start:end])
        result.append("</mark>")
        last_index = end
    result.append(text[last_index:])
    return "".join(result)


def build_highlight_map(text_length: int, matches: List[Tuple[int, int, int]], use_second_index: bool) -> Dict[int, Tuple[int, int]]:
    highlight_map: Dict[int, Tuple[int, int]] = {}
    for match in matches:
        start = match[1] if use_second_index else match[0]
        length = match[2]
        end = start + length
        if start >= text_length:
            continue
        end = min(end, text_length)
        highlight_map[start] = (end, length)
    return highlight_map


def generate_report(
    doc_a_name: str,
    doc_b_name: str,
    text_a: str,
    text_b: str,
    similarity: float,
    matches: List[Tuple[int, int, int]],
    min_length: int,
    output_dir: Path,
) -> None:
    highlight_map_a = build_highlight_map(len(text_a), matches, use_second_index=False)
    highlight_map_b = build_highlight_map(len(text_b), matches, use_second_index=True)

    highlighted_a = highlight_matches(text_a, matches, highlight_map_a)
    highlighted_b = highlight_matches(text_b, matches, highlight_map_b)

    filename = f"{doc_a_name}_vs_{doc_b_name}.html"
    report_path = output_dir / filename
    report_path.write_text(
        f"""<html><head><meta charset='utf-8'><title>Similarity Report {doc_a_name} vs {doc_b_name}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; }}
pre {{ background: #f4f4f4; padding: 1rem; white-space: pre-wrap; word-wrap: break-word; }}
mark {{ background: #fffd54; }}
</style>
</head><body>
<h1>Similarity Report</h1>
<p><strong>Documents:</strong> {doc_a_name} vs {doc_b_name}</p>
<p><strong>Similarity:</strong> {similarity:.2f}%</p>
<p><strong>Matching block threshold:</strong> {min_length} characters</p>
<h2>{doc_a_name}</h2>
<pre>{highlighted_a}</pre>
<h2>{doc_b_name}</h2>
<pre>{highlighted_b}</pre>
</body></html>
""",
        encoding="utf-8",
    )
    print(f"Report generated: {report_path}")


def main() -> None:
    args = parse_args()
    documents = load_documents(args.inputs)
    if len(documents) < 2:
        print("Need at least two documents to compare.")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    for (doc_a, text_a), (doc_b, text_b) in itertools.combinations(documents.items(), 2):
        similarity = compute_similarity(text_a, text_b)
        matches = find_matching_blocks(text_a, text_b, args.min_match_length)
        summary_rows.append((doc_a, doc_b, similarity, len(matches)))
        generate_report(doc_a, doc_b, text_a, text_b, similarity, matches, args.min_match_length, output_dir)

    summary_path = output_dir / "summary.csv"
    with summary_path.open("w", encoding="utf-8") as fh:
        fh.write("doc_a,doc_b,similarity_percent,matching_blocks\n")
        for row in summary_rows:
            fh.write(f"{row[0]},{row[1]},{row[2]:.2f},{row[3]}\n")
    print(f"Summary saved: {summary_path}")


if __name__ == "__main__":
    main()
