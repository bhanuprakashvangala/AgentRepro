#!/usr/bin/env python3
"""Spell checker with suggestions and custom dictionary support."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from spellchecker import SpellChecker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spell check text files with auto-correction suggestions")
    parser.add_argument("--input", nargs="+", required=True, help="Input text files to check")
    parser.add_argument("--custom-dict", help="Path to custom dictionary file (one word per line)")
    parser.add_argument(
        "--language",
        default="en",
        help="Dictionary language (default: en)",
    )
    parser.add_argument(
        "--max-suggestions",
        type=int,
        default=3,
        help="Maximum suggestions per misspelled word (default: 3)",
    )
    return parser.parse_args()


def load_text(files: Iterable[str]) -> str:
    content_parts: List[str] = []
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: file not found {path}")
            continue
        content_parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(content_parts)


def load_custom_dictionary(spell: SpellChecker, path: Optional[str]) -> None:
    if not path:
        return
    dict_path = Path(path)
    if not dict_path.exists():
        print(f"Warning: custom dictionary not found {dict_path}")
        return
    words = [line.strip() for line in dict_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    spell.word_frequency.load_words(words)


def spell_check_text(text: str, spell: SpellChecker, max_suggestions: int) -> List[str]:
    report: List[str] = []
    words = spell.split_words(text)
    misspelled = spell.unknown(words)
    if not misspelled:
        report.append("No spelling issues detected.")
        return report

    for word in sorted(misspelled):
        suggestions = spell.candidates(word)
        ranked = sorted(suggestions, key=lambda w: spell.word_probability(w), reverse=True)
        report.append(f"Misspelled: {word}")
        for suggestion in ranked[:max_suggestions]:
            if suggestion == word:
                continue
            report.append(f"  Suggestion: {suggestion}")
        report.append("")
    return report


def main() -> None:
    args = parse_args()
    text = load_text(args.input)
    if not text:
        print("No input text to process.")
        return

    spell = SpellChecker(language=args.language)
    load_custom_dictionary(spell, args.custom_dict)

    report = spell_check_text(text, spell, args.max_suggestions)
    print("\n".join(report))


if __name__ == "__main__":
    main()
