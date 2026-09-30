# Credit Card Validator

This is a command-line tool for validating credit card information based on common industry algorithms and standards.

**Disclaimer:** This tool is for educational purposes to demonstrate validation algorithms. **DO NOT** use this tool to store or process real, sensitive credit card information.

## Features

- **Luhn Algorithm Check**: Verifies the card number against the Luhn checksum formula to guard against simple typos.
- **Card Type Detection**: Identifies the card issuer (Visa, MasterCard, American Express) based on the number's prefix and length.
- **Expiration Date Validation**: Checks if the card's expiration date (in MM/YY format) has already passed.
- **Built-in Test Suite**: Includes a `--test` mode that runs a series of predefined test cases to verify the correctness of the validation logic.
- **No Dependencies**: Written in pure Python, requiring no external libraries.

## Usage

No installation is required beyond having a standard Python interpreter.

### 1. (Recommended) Run the Test Suite

To verify that the script is working correctly, run the built-in tests. This will check a variety of valid and invalid card numbers.

```bash
python card_validator.py --test
```

### 2. Validate a Specific Card Number

Use the `--card-number` (or `-cn`) and `--expiry` (or `-e`) flags to validate a specific card.

```bash
python card_validator.py --card-number "49927398716" --expiry "12/25"
```

#### Example Output

```
--- Validation Report ---
Card Number              : **** **** **** 8716
Card Type                : Visa
Luhn Algorithm Valid     : True
Expiration Date Valid    : True
Is Valid                 : True
-------------------------
```
