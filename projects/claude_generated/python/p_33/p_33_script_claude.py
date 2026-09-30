"""
Spell Checker with Auto-Correction Suggestions
Supports multiple libraries, correction suggestions, and custom dictionaries
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
import json

# Try to import both libraries
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from spellchecker import SpellChecker
    PYSPELLCHECKER_AVAILABLE = True
except ImportError:
    PYSPELLCHECKER_AVAILABLE = False


class SpellCheckerTool:
    """Spell checker with support for multiple backends and custom dictionaries"""

    def __init__(self, library: str = 'auto', custom_dict_path: str = None):
        """
        Initialize spell checker

        Args:
            library: 'textblob', 'pyspellchecker', or 'auto' (tries both)
            custom_dict_path: Path to JSON file with custom dictionary words
        """
        self.library = library
        self.custom_words: Set[str] = set()
        self.spell_checker = None

        # Load custom dictionary if provided
        if custom_dict_path:
            self.load_custom_dictionary(custom_dict_path)

        # Initialize the appropriate spell checker
        self._initialize_checker()

    def _initialize_checker(self):
        """Initialize the spell checking backend"""
        if self.library == 'auto':
            if PYSPELLCHECKER_AVAILABLE:
                self.library = 'pyspellchecker'
            elif TEXTBLOB_AVAILABLE:
                self.library = 'textblob'
            else:
                raise ImportError("Neither textblob nor pyspellchecker is available. Please install at least one.")

        if self.library == 'pyspellchecker':
            if not PYSPELLCHECKER_AVAILABLE:
                raise ImportError("pyspellchecker is not installed. Install with: pip install pyspellchecker")
            self.spell_checker = SpellChecker()
            # Add custom words to the spell checker
            if self.custom_words:
                self.spell_checker.word_frequency.load_words(self.custom_words)

        elif self.library == 'textblob':
            if not TEXTBLOB_AVAILABLE:
                raise ImportError("textblob is not installed. Install with: pip install textblob")
            # TextBlob doesn't need initialization, but we'll download required corpora
            try:
                # This will ensure the corpora are available
                TextBlob("test")
            except LookupError:
                print("Downloading required TextBlob corpora...")
                import nltk
                nltk.download('brown', quiet=True)
                nltk.download('punkt', quiet=True)

        else:
            raise ValueError(f"Unknown library: {self.library}. Use 'textblob', 'pyspellchecker', or 'auto'")

    def load_custom_dictionary(self, dict_path: str):
        """Load custom dictionary from JSON file"""
        try:
            with open(dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.custom_words = set(word.lower() for word in data)
                elif isinstance(data, dict) and 'words' in data:
                    self.custom_words = set(word.lower() for word in data['words'])
                else:
                    raise ValueError("Custom dictionary must be a JSON list or dict with 'words' key")
                print(f"Loaded {len(self.custom_words)} custom words from {dict_path}")
        except Exception as e:
            print(f"Error loading custom dictionary: {e}")
            self.custom_words = set()

    def is_correct(self, word: str) -> bool:
        """Check if a word is spelled correctly"""
        word_lower = word.lower()

        # Check custom dictionary first
        if word_lower in self.custom_words:
            return True

        if self.library == 'pyspellchecker':
            # In pyspellchecker, unknown() returns set of misspelled words
            return word_lower not in self.spell_checker.unknown([word_lower])

        elif self.library == 'textblob':
            blob = TextBlob(word)
            # If correction equals the word, it's correctly spelled
            return blob.correct().string.lower() == word_lower

        return False

    def get_suggestions(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Get correction suggestions for a misspelled word"""
        word_lower = word.lower()

        # If word is in custom dictionary, no suggestions needed
        if word_lower in self.custom_words:
            return []

        if self.library == 'pyspellchecker':
            candidates = self.spell_checker.candidates(word_lower)
            if candidates is None:
                return []
            # Filter out the original word and limit suggestions
            suggestions = [w for w in candidates if w != word_lower]
            return suggestions[:max_suggestions]

        elif self.library == 'textblob':
            blob = TextBlob(word)
            correction = blob.correct().string
            if correction.lower() != word_lower:
                return [correction]
            return []

        return []

    def check_text(self, text: str) -> List[Dict]:
        """
        Check spelling in text and return detailed results

        Returns:
            List of dicts with keys: 'word', 'correct', 'suggestions', 'position'
        """
        words = text.split()
        results = []
        position = 0

        for word in words:
            # Strip punctuation for checking
            clean_word = word.strip('.,!?;:"\'-()[]{}')
            if not clean_word or not clean_word.isalpha():
                position += len(word) + 1
                continue

            is_correct = self.is_correct(clean_word)
            suggestions = [] if is_correct else self.get_suggestions(clean_word)

            results.append({
                'word': clean_word,
                'original': word,
                'correct': is_correct,
                'suggestions': suggestions,
                'position': position
            })

            position += len(word) + 1

        return results

    def check_file(self, file_path: str) -> List[Dict]:
        """Check spelling in a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.check_text(text)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []

    def auto_correct_text(self, text: str) -> str:
        """Auto-correct text and return the corrected version"""
        if self.library == 'pyspellchecker':
            words = text.split()
            corrected_words = []

            for word in words:
                clean_word = word.strip('.,!?;:"\'-()[]{}')
                prefix = word[:len(word) - len(word.lstrip('.,!?;:"\'-()[]{}'))]
                suffix = word[len(clean_word) + len(prefix):]

                if clean_word and clean_word.isalpha() and not self.is_correct(clean_word):
                    suggestions = self.get_suggestions(clean_word, 1)
                    if suggestions:
                        corrected_words.append(prefix + suggestions[0] + suffix)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)

            return ' '.join(corrected_words)

        elif self.library == 'textblob':
            blob = TextBlob(text)
            return str(blob.correct())

        return text


def print_results(results: List[Dict], show_correct: bool = False):
    """Print spell check results in a formatted way"""
    misspelled_count = sum(1 for r in results if not r['correct'])

    print(f"\n{'='*70}")
    print(f"Spell Check Results")
    print(f"{'='*70}")
    print(f"Total words checked: {len(results)}")
    print(f"Misspelled words: {misspelled_count}")
    print(f"{'='*70}\n")

    if misspelled_count == 0:
        print("No spelling errors found!")
        return

    for result in results:
        if not result['correct'] or show_correct:
            status = "✓" if result['correct'] else "✗"
            print(f"{status} {result['word']}")

            if not result['correct'] and result['suggestions']:
                print(f"   Suggestions: {', '.join(result['suggestions'])}")
                print()


def main():
    parser = argparse.ArgumentParser(
        description='Spell Checker with Auto-Correction Suggestions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check spelling in text
  python spell_checker.py --text "This is a tesst with speling errors"

  # Check spelling in a file
  python spell_checker.py --file document.txt

  # Use specific library
  python spell_checker.py --text "tesst" --library pyspellchecker

  # Auto-correct text
  python spell_checker.py --text "Tesst sentance" --correct

  # Use custom dictionary
  python spell_checker.py --file doc.txt --custom-dict mywords.json
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', '-t', type=str, help='Text to check')
    input_group.add_argument('--file', '-f', type=str, help='File to check')

    # Configuration options
    parser.add_argument('--library', '-l',
                       choices=['auto', 'textblob', 'pyspellchecker'],
                       default='auto',
                       help='Spell checker library to use (default: auto)')

    parser.add_argument('--custom-dict', '-d', type=str,
                       help='Path to custom dictionary JSON file')

    parser.add_argument('--correct', '-c', action='store_true',
                       help='Auto-correct the text instead of just checking')

    parser.add_argument('--show-correct', '-s', action='store_true',
                       help='Show correctly spelled words in results')

    parser.add_argument('--max-suggestions', '-m', type=int, default=5,
                       help='Maximum number of suggestions per word (default: 5)')

    args = parser.parse_args()

    # Initialize spell checker
    try:
        checker = SpellCheckerTool(library=args.library, custom_dict_path=args.custom_dict)
        print(f"Using spell checker: {checker.library}")
    except (ImportError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Get text to check
    if args.text:
        text = args.text
        print(f"\nChecking text: '{text}'")
    else:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        print(f"\nChecking file: {args.file}")
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()

    # Perform spell check or correction
    if args.correct:
        corrected = checker.auto_correct_text(text)
        print(f"\n{'='*70}")
        print("Original text:")
        print(f"{'='*70}")
        print(text)
        print(f"\n{'='*70}")
        print("Corrected text:")
        print(f"{'='*70}")
        print(corrected)
        print()
    else:
        results = checker.check_text(text)
        print_results(results, show_correct=args.show_correct)


if __name__ == '__main__':
    main()
