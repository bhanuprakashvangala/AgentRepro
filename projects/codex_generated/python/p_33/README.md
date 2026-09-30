# Spell Checker with Suggestions

Checks text files for spelling mistakes using `pyspellchecker`, offers correction suggestions, and allows custom dictionary words.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python spell_checker.py --input article.txt notes.txt --custom-dict domain_words.txt --max-suggestions 5
```

Options:
- `--input`: One or more text files to scan.
- `--custom-dict`: Optional file containing additional valid words (one per line).
- `--language`: Dictionary language code (default `en`).
- `--max-suggestions`: Limit number of correction suggestions per misspelled word (default `3`).

The script prints misspelled words with ranked suggestions. If no spelling issues are found, it reports accordingly.
