"""
Credit Card Validator using Luhn Algorithm
Validates credit cards, detects card types, and validates expiration dates.
"""

from datetime import datetime
from typing import Tuple, Optional
import re


class CreditCardValidator:
    """
    Validates credit cards using Luhn algorithm and detects card types.
    """

    # Card type patterns (first digits and length)
    CARD_PATTERNS = {
        'Visa': {
            'prefixes': [r'^4'],
            'lengths': [13, 16, 19]
        },
        'MasterCard': {
            'prefixes': [r'^5[1-5]', r'^2[2-7]'],
            'lengths': [16]
        },
        'American Express': {
            'prefixes': [r'^3[47]'],
            'lengths': [15]
        },
        'Discover': {
            'prefixes': [r'^6011', r'^65', r'^64[4-9]', r'^622'],
            'lengths': [16, 19]
        },
        'Diners Club': {
            'prefixes': [r'^30[0-5]', r'^36', r'^38'],
            'lengths': [14]
        },
        'JCB': {
            'prefixes': [r'^35'],
            'lengths': [16]
        }
    }

    @staticmethod
    def clean_card_number(card_number: str) -> str:
        """
        Remove spaces, dashes, and other non-digit characters from card number.

        Args:
            card_number: Raw card number string

        Returns:
            Cleaned card number with only digits
        """
        return re.sub(r'\D', '', card_number)

    @staticmethod
    def luhn_checksum(card_number: str) -> bool:
        """
        Validate card number using Luhn algorithm (mod 10).

        The Luhn algorithm works as follows:
        1. Starting from the rightmost digit (check digit), double every second digit
        2. If doubling results in a number > 9, subtract 9
        3. Sum all digits
        4. If sum % 10 == 0, the number is valid

        Args:
            card_number: Card number as string (digits only)

        Returns:
            True if valid according to Luhn algorithm, False otherwise
        """
        if not card_number.isdigit():
            return False

        total = 0
        reverse_digits = card_number[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)

            # Double every second digit (odd indices in reversed string)
            if i % 2 == 1:
                n *= 2
                # If result > 9, subtract 9 (equivalent to summing digits)
                if n > 9:
                    n -= 9

            total += n

        return total % 10 == 0

    @classmethod
    def detect_card_type(cls, card_number: str) -> Optional[str]:
        """
        Detect the card type based on card number pattern.

        Args:
            card_number: Card number as string (digits only)

        Returns:
            Card type name or None if not recognized
        """
        card_len = len(card_number)

        for card_type, rules in cls.CARD_PATTERNS.items():
            # Check if length matches
            if card_len not in rules['lengths']:
                continue

            # Check if prefix matches
            for prefix_pattern in rules['prefixes']:
                if re.match(prefix_pattern, card_number):
                    return card_type

        return None

    @staticmethod
    def validate_expiration_date(month: int, year: int) -> bool:
        """
        Validate that the expiration date is in the future.

        Args:
            month: Expiration month (1-12)
            year: Expiration year (can be 2 or 4 digits)

        Returns:
            True if expiration date is valid and in the future
        """
        # Validate month
        if not (1 <= month <= 12):
            return False

        # Convert 2-digit year to 4-digit year
        if year < 100:
            current_year = datetime.now().year
            century = (current_year // 100) * 100
            year = century + year

            # Handle century boundary
            if year < current_year - 50:
                year += 100

        # Create expiration date (last day of expiration month)
        try:
            # Cards are valid through the last day of the expiration month
            if month == 12:
                exp_date = datetime(year + 1, 1, 1)
            else:
                exp_date = datetime(year, month + 1, 1)

            # Check if expiration date is in the future
            return exp_date > datetime.now()
        except ValueError:
            return False

    @classmethod
    def validate_card(cls, card_number: str, exp_month: Optional[int] = None,
                     exp_year: Optional[int] = None) -> Tuple[bool, dict]:
        """
        Comprehensive credit card validation.

        Args:
            card_number: Card number (can include spaces/dashes)
            exp_month: Optional expiration month
            exp_year: Optional expiration year

        Returns:
            Tuple of (is_valid, details_dict)
            details_dict contains:
                - card_number: Cleaned card number
                - card_type: Detected card type or None
                - luhn_valid: Boolean indicating Luhn validation
                - expiration_valid: Boolean if expiration provided, None otherwise
                - errors: List of error messages
        """
        errors = []
        cleaned_number = cls.clean_card_number(card_number)

        # Validate card number format
        if not cleaned_number:
            errors.append("Card number is empty")
            return False, {
                'card_number': cleaned_number,
                'card_type': None,
                'luhn_valid': False,
                'expiration_valid': None,
                'errors': errors
            }

        if not cleaned_number.isdigit():
            errors.append("Card number contains invalid characters")

        if len(cleaned_number) < 13 or len(cleaned_number) > 19:
            errors.append(f"Invalid card number length: {len(cleaned_number)}")

        # Luhn validation
        luhn_valid = cls.luhn_checksum(cleaned_number)
        if not luhn_valid:
            errors.append("Card number failed Luhn algorithm validation")

        # Detect card type
        card_type = cls.detect_card_type(cleaned_number)
        if not card_type:
            errors.append("Unable to detect card type")

        # Validate expiration date if provided
        expiration_valid = None
        if exp_month is not None and exp_year is not None:
            expiration_valid = cls.validate_expiration_date(exp_month, exp_year)
            if not expiration_valid:
                errors.append("Card has expired or invalid expiration date")

        is_valid = luhn_valid and card_type is not None and len(errors) == 0
        if exp_month is not None and exp_year is not None:
            is_valid = is_valid and expiration_valid

        return is_valid, {
            'card_number': cleaned_number,
            'card_type': card_type,
            'luhn_valid': luhn_valid,
            'expiration_valid': expiration_valid,
            'errors': errors if errors else None
        }


def format_card_number(card_number: str, card_type: Optional[str] = None) -> str:
    """
    Format card number with appropriate spacing for display.

    Args:
        card_number: Card number (digits only)
        card_type: Optional card type for type-specific formatting

    Returns:
        Formatted card number string
    """
    if card_type == 'American Express':
        # Format: XXXX XXXXXX XXXXX
        return f"{card_number[:4]} {card_number[4:10]} {card_number[10:]}"
    else:
        # Format: XXXX XXXX XXXX XXXX
        return ' '.join([card_number[i:i+4] for i in range(0, len(card_number), 4)])


def main():
    """
    Demo usage of the credit card validator.
    """
    print("=" * 60)
    print("Credit Card Validator - Demo")
    print("=" * 60)

    # Test cases
    test_cards = [
        {
            'number': '4532 1488 0343 6467',
            'month': 12,
            'year': 2025,
            'description': 'Valid Visa'
        },
        {
            'number': '5425233430109903',
            'month': 8,
            'year': 2026,
            'description': 'Valid MasterCard'
        },
        {
            'number': '378282246310005',
            'month': 6,
            'year': 2024,
            'description': 'American Express (expired)'
        },
        {
            'number': '6011111111111117',
            'month': 3,
            'year': 2027,
            'description': 'Valid Discover'
        },
        {
            'number': '4532148803436468',
            'month': 12,
            'year': 2025,
            'description': 'Invalid Luhn checksum'
        },
        {
            'number': '1234567890123456',
            'month': 12,
            'year': 2025,
            'description': 'Invalid card number'
        }
    ]

    validator = CreditCardValidator()

    for i, test in enumerate(test_cards, 1):
        print(f"\nTest {i}: {test['description']}")
        print("-" * 60)

        is_valid, details = validator.validate_card(
            test['number'],
            test['month'],
            test['year']
        )

        print(f"Card Number: {format_card_number(details['card_number'], details['card_type'])}")
        print(f"Card Type: {details['card_type'] or 'Unknown'}")
        print(f"Expiration: {test['month']:02d}/{test['year']}")
        print(f"Luhn Valid: {details['luhn_valid']}")
        print(f"Expiration Valid: {details['expiration_valid']}")
        print(f"Overall Valid: {is_valid}")

        if details['errors']:
            print(f"Errors: {', '.join(details['errors'])}")


if __name__ == '__main__':
    main()
