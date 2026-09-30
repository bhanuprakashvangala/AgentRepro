# Credit Card Validator

Validates credit card numbers with the Luhn algorithm, detects card type (Visa, MasterCard, Amex), and checks expiration dates.

## Setup
(Optional virtualenv)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install requirements (none beyond standard library).

## Usage
```bash
python credit_card_validator.py "4111 1111 1111 1111" --expiration 12/2099
```

The script prints a `CardValidationResult` dataclass instance with details on Luhn validity, card type, expiration status, and a summary message.

## Tests
```bash
python tests.py
```

The test suite covers Luhn validation, card type detection, expiration checks, and end-to-end scenarios.
