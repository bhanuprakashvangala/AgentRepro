import secrets
import string
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib


class PasswordStrengthChecker:
    """Check password strength based on entropy, patterns, and common passwords."""

    def __init__(self, wordlist_path: str = None):
        self.common_passwords = self._load_common_passwords(wordlist_path)

    def _load_common_passwords(self, wordlist_path: str) -> set:
        """Load common passwords from wordlist file."""
        if wordlist_path and Path(wordlist_path).exists():
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                return {line.strip().lower() for line in f if line.strip()}
        # Minimal built-in list if no wordlist provided
        return {
            'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
            'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou', 'master',
            'sunshine', 'ashley', 'bailey', 'shadow', 'superman', 'qazwsx',
            '123123', 'admin', 'welcome', 'login', 'passw0rd', 'football'
        }

    def calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits."""
        if not password:
            return 0.0

        # Determine character pool size
        pool_size = 0
        if re.search(r'[a-z]', password):
            pool_size += 26
        if re.search(r'[A-Z]', password):
            pool_size += 26
        if re.search(r'[0-9]', password):
            pool_size += 10
        if re.search(r'[^a-zA-Z0-9]', password):
            pool_size += 32  # Common special characters

        if pool_size == 0:
            return 0.0

        # Entropy = log2(pool_size^length)
        entropy = len(password) * math.log2(pool_size)
        return entropy

    def check_patterns(self, password: str) -> List[str]:
        """Detect common patterns that weaken passwords."""
        issues = []

        # Check for sequential characters
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            issues.append("Contains sequential letters")

        # Check for sequential numbers
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            issues.append("Contains sequential numbers")

        # Check for repeated characters
        if re.search(r'(.)\1{2,}', password):
            issues.append("Contains repeated characters")

        # Check for keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', 'qwertz', '1q2w3e']
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                issues.append(f"Contains keyboard pattern: {pattern}")

        # Check for common substitutions
        if re.search(r'[0o@][0o@]?', password.lower()) and 'oo' in password.lower().replace('0', 'o').replace('@', 'a'):
            issues.append("Uses common character substitutions")

        return issues

    def check_strength(self, password: str) -> Dict:
        """Comprehensive password strength check."""
        if not password:
            return {
                'score': 0,
                'strength': 'Very Weak',
                'entropy': 0.0,
                'length': 0,
                'issues': ['Password is empty'],
                'suggestions': ['Create a password']
            }

        score = 0
        issues = []
        suggestions = []

        # Check length
        length = len(password)
        if length < 8:
            issues.append(f"Too short (minimum 8 characters)")
            suggestions.append("Use at least 12 characters")
        elif length < 12:
            score += 1
            suggestions.append("Consider using 16+ characters for better security")
        elif length < 16:
            score += 2
        else:
            score += 3

        # Calculate entropy
        entropy = self.calculate_entropy(password)
        if entropy < 28:
            issues.append("Low entropy (weak randomness)")
        elif entropy < 36:
            score += 1
        elif entropy < 60:
            score += 2
        else:
            score += 3

        # Check character variety
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

        char_variety = sum([has_lower, has_upper, has_digit, has_special])

        if char_variety < 3:
            issues.append("Lacks character variety")
            if not has_upper:
                suggestions.append("Add uppercase letters")
            if not has_digit:
                suggestions.append("Add numbers")
            if not has_special:
                suggestions.append("Add special characters")
        else:
            score += char_variety - 2

        # Check for common passwords
        if password.lower() in self.common_passwords:
            issues.append("Found in common password list")
            score = max(0, score - 5)

        # Check for patterns
        pattern_issues = self.check_patterns(password)
        if pattern_issues:
            issues.extend(pattern_issues)
            score = max(0, score - len(pattern_issues))

        # Determine strength rating
        if score <= 2:
            strength = 'Very Weak'
        elif score <= 4:
            strength = 'Weak'
        elif score <= 6:
            strength = 'Moderate'
        elif score <= 8:
            strength = 'Strong'
        else:
            strength = 'Very Strong'

        return {
            'score': score,
            'strength': strength,
            'entropy': round(entropy, 2),
            'length': length,
            'has_lowercase': has_lower,
            'has_uppercase': has_upper,
            'has_digits': has_digit,
            'has_special': has_special,
            'issues': issues if issues else ['None'],
            'suggestions': suggestions if suggestions else ['Password meets strength requirements']
        }


class PasswordGenerator:
    """Generate secure passwords using the secrets library."""

    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate(
        self,
        length: int = 16,
        use_lowercase: bool = True,
        use_uppercase: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
        exclude_chars: str = "",
        must_include: str = "",
        min_lowercase: int = 0,
        min_uppercase: int = 0,
        min_digits: int = 0,
        min_special: int = 0
    ) -> str:
        """
        Generate a secure password with custom rules.

        Args:
            length: Total password length
            use_lowercase: Include lowercase letters
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            use_special: Include special characters
            exclude_chars: Characters to exclude
            must_include: Specific characters that must be included
            min_lowercase: Minimum number of lowercase letters
            min_uppercase: Minimum number of uppercase letters
            min_digits: Minimum number of digits
            min_special: Minimum number of special characters
        """
        if length < 4:
            raise ValueError("Password length must be at least 4 characters")

        # Build character pool
        char_pool = ""
        if use_lowercase:
            char_pool += self.lowercase
        if use_uppercase:
            char_pool += self.uppercase
        if use_digits:
            char_pool += self.digits
        if use_special:
            char_pool += self.special

        if not char_pool:
            raise ValueError("At least one character type must be enabled")

        # Remove excluded characters
        if exclude_chars:
            char_pool = ''.join(c for c in char_pool if c not in exclude_chars)

        if not char_pool:
            raise ValueError("Character pool is empty after exclusions")

        # Check if minimum requirements are achievable
        total_min = min_lowercase + min_uppercase + min_digits + min_special + len(must_include)
        if total_min > length:
            raise ValueError(f"Minimum requirements ({total_min}) exceed password length ({length})")

        # Generate password with requirements
        password_chars = []

        # Add required minimums
        if min_lowercase > 0:
            pool = ''.join(c for c in self.lowercase if c not in exclude_chars)
            password_chars.extend(secrets.choice(pool) for _ in range(min_lowercase))

        if min_uppercase > 0:
            pool = ''.join(c for c in self.uppercase if c not in exclude_chars)
            password_chars.extend(secrets.choice(pool) for _ in range(min_uppercase))

        if min_digits > 0:
            pool = ''.join(c for c in self.digits if c not in exclude_chars)
            password_chars.extend(secrets.choice(pool) for _ in range(min_digits))

        if min_special > 0:
            pool = ''.join(c for c in self.special if c not in exclude_chars)
            password_chars.extend(secrets.choice(pool) for _ in range(min_special))

        # Add must-include characters
        if must_include:
            password_chars.extend(list(must_include))

        # Fill remaining length with random characters from pool
        remaining = length - len(password_chars)
        password_chars.extend(secrets.choice(char_pool) for _ in range(remaining))

        # Shuffle using secrets for cryptographic randomness
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        return ''.join(password_chars)

    def generate_passphrase(
        self,
        num_words: int = 4,
        separator: str = "-",
        capitalize: bool = True,
        add_number: bool = True
    ) -> str:
        """Generate a memorable passphrase using word list."""
        # Built-in word list (EFF-inspired)
        words = [
            'ability', 'able', 'about', 'above', 'accept', 'account', 'achieve', 'action',
            'active', 'actual', 'address', 'admit', 'advance', 'advice', 'affect', 'afford',
            'afraid', 'after', 'again', 'against', 'agent', 'agree', 'ahead', 'allow',
            'almost', 'alone', 'along', 'already', 'always', 'amount', 'animal', 'annual',
            'another', 'answer', 'anyone', 'anything', 'appear', 'apply', 'approach', 'area',
            'argue', 'around', 'arrive', 'artist', 'assume', 'attack', 'attempt', 'attend',
            'author', 'avoid', 'aware', 'away', 'baby', 'back', 'balance', 'ball', 'bank',
            'base', 'basic', 'basis', 'battle', 'beach', 'bear', 'beat', 'beautiful',
            'because', 'become', 'before', 'begin', 'behavior', 'behind', 'believe', 'benefit',
            'best', 'better', 'between', 'beyond', 'bill', 'billion', 'bird', 'birth',
            'black', 'blood', 'blue', 'board', 'body', 'book', 'born', 'both', 'bottom',
            'box', 'boy', 'brain', 'branch', 'bread', 'break', 'bright', 'bring', 'brother',
            'budget', 'build', 'building', 'business', 'busy', 'button', 'buy', 'call',
            'camera', 'campaign', 'cancer', 'capital', 'card', 'care', 'career', 'carry',
            'case', 'catch', 'cause', 'cell', 'center', 'central', 'century', 'certain',
            'chair', 'challenge', 'chance', 'change', 'character', 'charge', 'check', 'child',
            'choice', 'choose', 'church', 'citizen', 'city', 'civil', 'claim', 'class',
            'clear', 'close', 'coach', 'cold', 'collection', 'college', 'color', 'come',
            'commercial', 'common', 'community', 'company', 'compare', 'computer', 'concern',
            'condition', 'conference', 'congress', 'consider', 'consumer', 'contain', 'continue'
        ]

        selected_words = [secrets.choice(words) for _ in range(num_words)]

        if capitalize:
            selected_words = [word.capitalize() for word in selected_words]

        passphrase = separator.join(selected_words)

        if add_number:
            passphrase += separator + str(secrets.randbelow(900) + 100)

        return passphrase


def main():
    """Demo and interactive CLI."""
    print("=== Password Strength Checker and Generator ===\n")

    # Initialize
    checker = PasswordStrengthChecker()
    generator = PasswordGenerator()

    # Demo: Generate and check passwords
    print("1. Generating Strong Password:")
    strong_pw = generator.generate(length=16)
    print(f"   Password: {strong_pw}")
    result = checker.check_strength(strong_pw)
    print(f"   Strength: {result['strength']} (Score: {result['score']}, Entropy: {result['entropy']} bits)")
    print()

    print("2. Generating Passphrase:")
    passphrase = generator.generate_passphrase(num_words=4)
    print(f"   Passphrase: {passphrase}")
    result = checker.check_strength(passphrase)
    print(f"   Strength: {result['strength']} (Score: {result['score']}, Entropy: {result['entropy']} bits)")
    print()

    print("3. Checking Weak Passwords:")
    weak_passwords = ['password123', '12345678', 'qwerty', 'abc123']
    for pwd in weak_passwords:
        result = checker.check_strength(pwd)
        print(f"   '{pwd}': {result['strength']} - Issues: {', '.join(result['issues'][:2])}")
    print()

    print("4. Custom Password with Rules:")
    custom_pw = generator.generate(
        length=20,
        min_lowercase=5,
        min_uppercase=5,
        min_digits=3,
        min_special=2,
        exclude_chars='O0Il1'
    )
    print(f"   Password: {custom_pw}")
    result = checker.check_strength(custom_pw)
    print(f"   Strength: {result['strength']} (Entropy: {result['entropy']} bits)")
    print()

    # Interactive mode
    print("\n=== Interactive Mode ===")
    while True:
        print("\nOptions:")
        print("  1. Generate password")
        print("  2. Generate passphrase")
        print("  3. Check password strength")
        print("  4. Exit")

        choice = input("\nChoose option (1-4): ").strip()

        if choice == '1':
            try:
                length = int(input("Length (default 16): ").strip() or "16")
                password = generator.generate(length=length)
                print(f"\nGenerated: {password}")
                result = checker.check_strength(password)
                print(f"Strength: {result['strength']} ({result['entropy']} bits entropy)")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '2':
            try:
                num_words = int(input("Number of words (default 4): ").strip() or "4")
                passphrase = generator.generate_passphrase(num_words=num_words)
                print(f"\nGenerated: {passphrase}")
                result = checker.check_strength(passphrase)
                print(f"Strength: {result['strength']} ({result['entropy']} bits entropy)")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == '3':
            password = input("Enter password to check: ").strip()
            result = checker.check_strength(password)
            print(f"\n=== Analysis ===")
            print(f"Strength: {result['strength']}")
            print(f"Score: {result['score']}/10")
            print(f"Entropy: {result['entropy']} bits")
            print(f"Length: {result['length']} characters")
            print(f"Lowercase: {'Yes' if result['has_lowercase'] else 'No'}")
            print(f"Uppercase: {'Yes' if result['has_uppercase'] else 'No'}")
            print(f"Digits: {'Yes' if result['has_digits'] else 'No'}")
            print(f"Special: {'Yes' if result['has_special'] else 'No'}")
            print(f"\nIssues: {', '.join(result['issues'])}")
            print(f"Suggestions: {', '.join(result['suggestions'])}")

        elif choice == '4':
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
