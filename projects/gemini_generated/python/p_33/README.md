# Spell Checker with Auto-correction

This is a command-line tool that checks a text file for spelling errors, provides auto-correction suggestions, and supports custom dictionaries. It is built using the `pyspellchecker` library.

## Features

- **Error Detection**: Identifies words that are not in the standard English dictionary.
- **Correction Suggestions**: For each misspelled word, it suggests the most likely correction and provides a list of other potential candidates.
- **Custom Dictionary**: You can provide a custom dictionary file (one word per line) to include proper nouns, technical terms, or other words that should not be flagged as errors.
- **Reproducible Demo**: Includes a `--demo` mode that automatically generates a sample text file with errors and a custom dictionary to provide a quick and easy end-to-end test.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Recommended) Run the Demo:**
    This is the best way to see the tool in action. It will create `sample.txt` and `custom_dict.txt` and then run the analysis.
    ```bash
    python spell_checker.py --demo
    ```

4.  **Check Your Own File:**
    Provide the path to any text file.
    ```bash
    python spell_checker.py /path/to/your/document.txt
    ```

5.  **Use a Custom Dictionary:**
    Create a text file with one word per line that you want to be considered correct. Then, use the `--custom-dict` flag.
    ```bash
    python spell_checker.py your_document.txt --custom-dict your_words.txt
    ```

## Example Demo Output

Running the demo will produce a report similar to this:

```
--- Spell Check Report for: sample.txt ---
Successfully loaded custom dictionary: custom_dict.txt

Found 4 misspelled word(s):

  - Word:      'documant'
    Correction:  'document'
    Suggestions: ['document']

  - Word:      'mispeled'
    Correction:  'misspelled'
    Suggestions: ['misspelled']

  - Word:      'severel'
    Correction:  'several'
    Suggestions: ['several']

  - Word:      'smaple'
    Correction:  'sample'
    Suggestions: ['sample']

--- End of Report ---
```
Notice that "gemini" is not flagged as an error because it was included in the custom dictionary.
