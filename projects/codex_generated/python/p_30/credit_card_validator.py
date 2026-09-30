#!/usr/bin/env python3
"""Credit card validation utility with Luhn algorithm and card type detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

CARD_PATTERNS = {
    "visa": re.compile(r"^4[0-9]{12}(?:[0-9]{3})?(?:[0-9]{3})?$"),
    "mastercard": re.compile(r"^(?:5[1-5][0-9]{14}|2(2[2-9][0-9]{12}|[3-6][0-9]{13}|7[01][0-9]{12}|720[0-9]{12}))$"),
    "amex": re.compile(r"^3[47][0-9]{13}$"),
}


@dataclass
class CardValidationResult:
    number: str
    card_type: Optional[str]
    luhn_valid: bool
    expiration_valid: bool
    is_valid: bool
    message: str


def luhn_checksum(number: str) -> int:
    digits = [int(ch) for ch in number if ch.isdigit()]
    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10


def passes_luhn(number: str) -> bool:
    sanitized = re.sub(r"[^0-9]", "", number)
    if not sanitized:
        return False
    return luhn_checksum(sanitized) == 0


def detect_card_type(number: str) -> Optional[str]:
    sanitized = re.sub(r"[^0-9]", "", number)
    for card_type, pattern in CARD_PATTERNS.items():
        if pattern.match(sanitized):
            return card_type
    return None


def validate_expiration(expiration: str) -> bool:
    """Validate expiration date in MM/YY or MM/YYYY."""
    try:
        if re.match(r"^(0[1-9]|1[0-2])/\d{2}$", expiration):
            exp_date = datetime.strptime(expiration, "%m/%y")
        elif re.match(r"^(0[1-9]|1[0-2])/\d{4}$", expiration):
            exp_date = datetime.strptime(expiration, "%m/%Y")
        else:
            return False
    except ValueError:
        return False

    now = datetime.now()
    # Set expiry to last day of month
    year = exp_date.year
    month = exp_date.month
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    next_month_start = datetime(year, month, 1)
    return next_month_start > now


def validate_card(number: str, expiration: Optional[str] = None) -> CardValidationResult:
    sanitized = re.sub(r"[^0-9]", "", number)
    card_type = detect_card_type(sanitized)
    luhn_valid = passes_luhn(sanitized)
    expiration_valid = True
    if expiration is not None:
        expiration_valid = validate_expiration(expiration)

    if not sanitized:
        message = "Card number is required"
    elif card_type is None:
        message = "Unknown or unsupported card type"
    elif not luhn_valid:
        message = "Failed Luhn checksum"
    elif not expiration_valid:
        message = "Card is expired or expiration format invalid"
    else:
        message = "Card is valid"

    is_valid = card_type is not None and luhn_valid and expiration_valid
    return CardValidationResult(
        number=sanitized,
        card_type=card_type,
        luhn_valid=luhn_valid,
        expiration_valid=expiration_valid,
        is_valid=is_valid,
        message=message,
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate credit card numbers (Luhn + type + expiration)")
    parser.add_argument("number", help="Credit card number")
    parser.add_argument("--expiration", help="Expiration date MM/YY or MM/YYYY")
    args = parser.parse_args()
    result = validate_card(args.number, args.expiration)
    print(result)
