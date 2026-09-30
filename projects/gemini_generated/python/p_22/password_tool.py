import secrets
import string
import math
import argparse
import getpass
import os

COMMON_PASSWORDS_FILE = "common_passwords.txt"

def generate_common_passwords_list(filename=COMMON_PASSWORDS_FILE):
    """Creates a small, sample list of common passwords for demonstration."""
    if os.path.exists(filename):
        return
    print(f"Generating common password list: {filename}")
    common_passwords = [
        "password", "123456", "123456789", "qwerty", "111111", "12345678",
        "dragon", "pussy", "12345", "123123", "football", "iloveyou", "admin",
        "password123", "secret", "sunshine", "monkey"
    ]
    with open(filename, 'w') as f:
        for pwd in common_passwords:
            f.write(pwd + '\n')

def load_common_passwords(filename=COMMON_PASSWORDS_FILE):
    """Loads the common password list into a set for fast lookups."""
    try:
        with open(filename, 'r') as f:
            return {line.strip().lower() for line in f}
    except FileNotFoundError:
        return set()

def generate_password(length, use_upper, use_digits, use_symbols):
    """Generates a cryptographically secure password."""
    alphabet = string.ascii_lowercase
    if use_upper: alphabet += string.ascii_uppercase
    if use_digits: alphabet += string.digits
    if use_symbols: alphabet += string.punctuation

    if not alphabet:
        print("Error: Cannot generate a password with an empty character set.")
        return None

    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure the password meets the complexity requirements if specified
        if (not use_upper or any(c in string.ascii_uppercase for c in password)) and \
           (not use_digits or any(c in string.digits for c in password)) and \
           (not use_symbols or any(c in string.punctuation for c in password)):
            return password

def check_password_strength(password, common_passwords):
    """Analyzes a password and prints a detailed strength report."""
    print("\n--- Password Strength Analysis ---")
    score = 0
    feedback = []

    # 1. Length check
    if len(password) >= 12: score += 2
    elif len(password) >= 8: score += 1
    feedback.append(f"Length: {len(password)} (>=12 is recommended)")

    # 2. Character variety check
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    variety = sum([has_lower, has_upper, has_digit, has_symbol])
    if variety >= 4: score += 2
    elif variety >= 3: score += 1
    feedback.append(f"Character Variety: {variety}/4 (lowercase, uppercase, digits, symbols)")

    # 3. Common password check
    if password.lower() in common_passwords:
        score = 0 # Overrule score if it's a common password
        feedback.append("CRITICAL: This is a very common password!")
    
    # 4. Entropy calculation
    pool_size = 0
    if has_lower: pool_size += 26
    if has_upper: pool_size += 26
    if has_digit: pool_size += 10
    if has_symbol: pool_size += 32 # Approximate size of string.punctuation
    
    entropy = 0
    if pool_size > 0:
        entropy = len(password) * math.log2(pool_size)
        feedback.append(f"Entropy: {entropy:.2f} bits")
        if entropy >= 128: score += 3
        elif entropy >= 60: score += 2
        elif entropy >= 40: score += 1

    # Final assessment
    if score >= 7: strength = "Very Strong"
    elif score >= 5: strength = "Strong"
    elif score >= 3: strength = "Moderate"
    elif score >= 1: strength = "Weak"
    else: strength = "Very Weak"
    
    if password.lower() in common_passwords: strength = "Very Weak"

    print(f"\nOverall Strength: {strength}")
    print("\nDetails:")
    for item in feedback:
        print(f"  - {item}")
    print("--------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and check password strength.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Generate Command ---
    gen_parser = subparsers.add_parser("generate", help="Generate a new secure password.")
    gen_parser.add_argument("-l", "--length", type=int, default=16, help="Length of the password (default: 16).")
    gen_parser.add_argument("--no-upper", action="store_false", dest="upper", help="Exclude uppercase letters.")
    gen_parser.add_argument("--no-digits", action="store_false", dest="digits", help="Exclude digits.")
    gen_parser.add_argument("--no-symbols", action="store_false", dest="symbols", help="Exclude symbols.")

    # --- Check Command ---
    check_parser = subparsers.add_parser("check", help="Check the strength of a password.")

    args = parser.parse_args()

    if args.command == "generate":
        new_password = generate_password(args.length, args.upper, args.digits, args.symbols)
        if new_password:
            print(f"Generated Password: {new_password}")
    elif args.command == "check":
        generate_common_passwords_list()
        common_set = load_common_passwords()
        try:
            password_to_check = getpass.getpass("Enter password to check: ")
            if password_to_check:
                check_password_strength(password_to_check, common_set)
            else:
                print("Password cannot be empty.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
