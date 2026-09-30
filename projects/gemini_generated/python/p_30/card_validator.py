import re
import argparse
from datetime import datetime

# --- Card Type Definitions ---
# (Regex pattern, Card Type Name)
CARD_TYPES = [
    (re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$"), "Visa"),
    (re.compile(r"^3[47][0-9]{13}$"), "American Express"),
    (re.compile(r"^5[1-5][0-9]{14}$"), "MasterCard"),
]

def luhn_checksum_is_valid(card_number: str) -> bool:
    """Checks if a card number is valid using the Luhn algorithm."""
    try:
        digits = [int(d) for d in card_number]
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled if doubled < 10 else (doubled - 9)
            else:
                checksum += digit
        return checksum % 10 == 0
    except (ValueError, TypeError):
        return False

def detect_card_type(card_number: str) -> str:
    """Detects the card type from its number."""
    for pattern, name in CARD_TYPES:
        if pattern.match(card_number):
            return name
    return "Unknown"

def expiry_date_is_valid(expiry_str: str) -> bool:
    """Checks if an expiry date string (MM/YY) is in the future."""
    match = re.match(r"^(0[1-9]|1[0-2])/([0-9]{2})$", expiry_str)
    if not match:
        return False
    
    exp_month, exp_year_short = int(match.group(1)), int(match.group(2))
    exp_year = 2000 + exp_year_short
    
    now = datetime.now()
    # The card is valid through the last day of its expiration month
    # So, if the current month is the expiration month, it's still valid.
    if exp_year > now.year:
        return True
    if exp_year == now.year and exp_month >= now.month:
        return True
    
    return False

def validate_card(card_number: str, expiry_date: str):
    """Performs a full validation of a credit card."""
    # Sanitize card number by removing non-digit characters
    sanitized_number = re.sub(r'\D', '', card_number)

    luhn_valid = luhn_checksum_is_valid(sanitized_number)
    card_type = detect_card_type(sanitized_number)
    expiry_valid = expiry_date_is_valid(expiry_date)

    return {
        "card_number": f"**** **** **** {sanitized_number[-4:]}",
        "card_type": card_type,
        "luhn_algorithm_valid": luhn_valid,
        "expiration_date_valid": expiry_valid,
        "is_valid": luhn_valid and expiry_valid and card_type != "Unknown"
    }

def run_tests():
    """Runs a comprehensive suite of test cases."""
    print("--- Running Test Suite ---")
    test_cases = [
        # Valid Visa
        {"card": "49927398716", "expiry": "12/25", "luhn": True, "type": "Visa", "expiry_ok": True},
        # Valid Amex
        {"card": "378282246310005", "expiry": "11/28", "luhn": True, "type": "American Express", "expiry_ok": True},
        # Valid MasterCard
        {"card": "5105105105105100", "expiry": "10/27", "luhn": True, "type": "MasterCard", "expiry_ok": True},
        # Invalid Luhn
        {"card": "49927398717", "expiry": "12/25", "luhn": False, "type": "Visa", "expiry_ok": True},
        # Expired Date
        {"card": "49927398716", "expiry": "01/20", "luhn": True, "type": "Visa", "expiry_ok": False},
        # Invalid Date Format
        {"card": "49927398716", "expiry": "13/25", "luhn": True, "type": "Visa", "expiry_ok": False},
        # Unknown Type
        {"card": "1234567890123452", "expiry": "12/25", "luhn": True, "type": "Unknown", "expiry_ok": True},
    ]
    passed = 0
    for i, case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: Card ending in ...{case['card'][-4:]}")
        results = validate_card(case['card'], case['expiry'])
        try:
            assert results['luhn_algorithm_valid'] == case['luhn']
            assert results['card_type'] == case['type']
            assert results['expiration_date_valid'] == case['expiry_ok']
            print("  -> PASSED")
            passed += 1
        except AssertionError:
            print(f"  -> FAILED: Expected (luhn: {case['luhn']}, type: {case['type']}, expiry: {case['expiry_ok']}), Got {results}")
    
    print(f"\n--- Test Summary: {passed}/{len(test_cases)} Passed ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Credit Card Validator using Luhn Algorithm.")
    parser.add_argument("--test", action="store_true", help="Run the built-in test suite.")
    parser.add_argument("-cn", "--card-number", help="The card number to validate.")
    parser.add_argument("-e", "--expiry", help="The expiration date in MM/YY format.")
    args = parser.parse_args()

    if args.test:
        run_tests()
    elif args.card_number and args.expiry:
        validation_results = validate_card(args.card_number, args.expiry)
        print("\n--- Validation Report ---")
        for key, value in validation_results.items():
            print(f"{key.replace('_', ' ').title():<25}: {value}")
        print("-------------------------")
    else:
        print("Please either run with --test or provide both --card-number and --expiry.")
        parser.print_help()
