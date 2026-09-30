import argparse
import os
import re
from spellchecker import SpellChecker

# --- Default filenames for demo mode ---
DEMO_TEXT_FILE = "sample.txt"
DEMO_DICT_FILE = "custom_dict.txt"

def generate_sample_files():
    """Generates a sample text file and a custom dictionary for the demo."""
    # Create sample text with errors
    if not os.path.exists(DEMO_TEXT_FILE):
        print(f"Generating sample file: {DEMO_TEXT_FILE}")
        with open(DEMO_TEXT_FILE, 'w') as f:
            f.write("This is a smaple documant with severel mispeled wordz. "
                    "We will also test a custom word like Gemini, which shoud not be flagged.")
    
    # Create custom dictionary
    if not os.path.exists(DEMO_DICT_FILE):
        print(f"Generating custom dictionary: {DEMO_DICT_FILE}")
        with open(DEMO_DICT_FILE, 'w') as f:
            f.write("Gemini\n") # Add custom words, one per line

def check_spelling(file_path, custom_dict_path=None):
    """Checks the spelling of a text file and prints a report."""
    print(f"\n--- Spell Check Report for: {file_path} ---")
    
    try:
        with open(file_path, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return

    # Initialize SpellChecker
    spell = SpellChecker()

    # Load custom dictionary if provided
    if custom_dict_path:
        try:
            spell.word_frequency.load_text_file(custom_dict_path)
            print(f"Successfully loaded custom dictionary: {custom_dict_path}")
        except FileNotFoundError:
            print(f"[WARNING] Custom dictionary not found at: {custom_dict_path}")

    # Find misspelled words
    # Use regex to split text into words
    words = re.findall(r'\b\w+\b', text.lower())
    misspelled = spell.unknown(words)

    if not misspelled:
        print("\nNo spelling errors found!")
    else:
        print(f"\nFound {len(misspelled)} misspelled word(s):")
        for word in sorted(list(misspelled)):
            correction = spell.correction(word)
            candidates = list(spell.candidates(word))
            print(f"\n  - Word:      '{word}'")
            print(f"    Correction:  '{correction}'")
            print(f"    Suggestions: {candidates}")
    
    print("\n--- End of Report ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check spelling in a text file.")
    parser.add_argument("file", nargs='?', help="Path to the text file to check.")
    parser.add_argument("-d", "--custom-dict", help="Path to a custom dictionary file (one word per line).")
    parser.add_argument("--demo", action="store_true", help="Run a demo with sample files.")
    args = parser.parse_args()

    if args.demo:
        generate_sample_files()
        check_spelling(DEMO_TEXT_FILE, DEMO_DICT_FILE)
    elif args.file:
        check_spelling(args.file, args.custom_dict)
    else:
        print("Please provide a file to check or use the --demo flag.")
        parser.print_help()
