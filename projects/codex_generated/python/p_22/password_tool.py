#!/usr/bin/env python3
"""Password strength checker and generator with entropy estimates and wordlist detection."""

from __future__ import annotations

import argparse
import math
import secrets
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

DEFAULT_WORDLIST_PATH = Path(__file__).with_name("common_passwords.txt")


@dataclass
class StrengthReport:
    password: str
    length: int
    entropy: float
    character_sets: Dict[str, bool]
    common_password: bool
    suggestions: List[str]


class PasswordWordlist:
    def __init__(self, words: Iterable[str]) -> None:
        self._words = set(word.strip().lower() for word in words if word.strip())

    @classmethod
    def from_file(cls, path: Path) -> "PasswordWordlist":
        if not path.exists():
            return cls([])
        return cls(path.read_text(encoding="utf-8", errors="ignore").splitlines())

    def contains(self, password: str) -> bool:
        return password.lower() in self._words


def calculate_entropy(password: str, character_sets: Dict[str, bool]) -> float:
    unique_pool = 0
    if character_sets["lower"]:
        unique_pool += 26
    if character_sets["upper"]:
        unique_pool += 26
    if character_sets["digits"]:
        unique_pool += 10
    if character_sets["symbols"]:
        unique_pool += len(string.punctuation)

    if unique_pool == 0:
        unique_pool = len(set(password)) or 1
    entropy = len(password) * math.log2(unique_pool)
    return entropy


def analyze_password(password: str, wordlist: PasswordWordlist) -> StrengthReport:
    char_sets = {
        "lower": any(c.islower() for c in password),
        "upper": any(c.isupper() for c in password),
        "digits": any(c.isdigit() for c in password),
        "symbols": any(c in string.punctuation for c in password),
    }
    entropy = calculate_entropy(password, char_sets)
    is_common = wordlist.contains(password)

    suggestions: List[str] = []
    if len(password) < 12:
        suggestions.append("Use at least 12 characters")
    if not char_sets["upper"]:
        suggestions.append("Add uppercase letters")
    if not char_sets["lower"]:
        suggestions.append("Add lowercase letters")
    if not char_sets["digits"]:
        suggestions.append("Include digits")
    if not char_sets["symbols"]:
        suggestions.append("Include special characters")
    if entropy < 60:
        suggestions.append("Increase length/complexity to raise entropy above 60 bits")
    if is_common:
        suggestions.append("Avoid common or compromised passwords")

    return StrengthReport(
        password=password,
        length=len(password),
        entropy=entropy,
        character_sets=char_sets,
        common_password=is_common,
        suggestions=suggestions,
    )


def generate_password(
    length: int,
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
) -> str:
    pools = []
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(string.punctuation)

    if not pools:
        raise ValueError("At least one character set must be enabled for generation")

    # Ensure that generated password contains at least one character from each selected set.
    password_chars = [secrets.choice(pool) for pool in pools]
    remaining_length = max(length - len(password_chars), 0)
    combined_pool = "".join(pools)
    password_chars.extend(secrets.choice(combined_pool) for _ in range(remaining_length))
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars[:length])


def load_wordlist(path: Optional[str]) -> PasswordWordlist:
    if path:
        return PasswordWordlist.from_file(Path(path))
    if DEFAULT_WORDLIST_PATH.exists():
        return PasswordWordlist.from_file(DEFAULT_WORDLIST_PATH)
    return PasswordWordlist([])


def cmd_check(args: argparse.Namespace) -> None:
    wordlist = load_wordlist(args.wordlist)
    password = args.password
    if password is None:
        password = input("Enter password to check: ")
    report = analyze_password(password, wordlist)
    print(f"Password length: {report.length}")
    print(f"Entropy estimate: {report.entropy:.2f} bits")
    print(f"Contains lowercase: {report.character_sets['lower']}")
    print(f"Contains uppercase: {report.character_sets['upper']}")
    print(f"Contains digits: {report.character_sets['digits']}")
    print(f"Contains symbols: {report.character_sets['symbols']}")
    print(f"Common password: {report.common_password}")
    if report.suggestions:
        print("Suggestions:")
        for suggestion in report.suggestions:
            print(f"  - {suggestion}")
    else:
        print("No suggestions. Password appears strong.")


def cmd_generate(args: argparse.Namespace) -> None:
    password = generate_password(
        length=args.length,
        use_upper=not args.no_upper,
        use_lower=not args.no_lower,
        use_digits=not args.no_digits,
        use_symbols=not args.no_symbols,
    )
    print(password)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Password strength checker and generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Evaluate password strength")
    check_parser.add_argument("--password", help="Password to evaluate (prompts if omitted)")
    check_parser.add_argument("--wordlist", help="Path to common password wordlist")
    check_parser.set_defaults(func=cmd_check)

    gen_parser = subparsers.add_parser("generate", help="Generate a strong password")
    gen_parser.add_argument("--length", type=int, default=16, help="Password length (default 16)")
    gen_parser.add_argument("--no-upper", action="store_true", help="Exclude uppercase letters")
    gen_parser.add_argument("--no-lower", action="store_true", help="Exclude lowercase letters")
    gen_parser.add_argument("--no-digits", action="store_true", help="Exclude digits")
    gen_parser.add_argument("--no-symbols", action="store_true", help="Exclude punctuation symbols")
    gen_parser.set_defaults(func=cmd_generate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
