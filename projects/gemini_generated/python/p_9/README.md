# PDF Text Extraction and Analysis Tool

This project is a Python tool that extracts text from a PDF document, performs a basic Natural Language Processing (NLP) analysis (word count and frequency), and saves the results to a JSON file.

## Features

- **Sample PDF Generation**: Automatically creates a `sample.pdf` file using `reportlab` for immediate, reproducible testing.
- **Text Extraction**: Uses the `pdfplumber` library to accurately extract text from all pages of the PDF.
- **Basic NLP Analysis**: Calculates the total word count, unique word count, and the frequency of the most common words.
- **JSON Export**: Saves the structured analysis results into a human-readable JSON file (`analysis_results.json`).

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

3.  **Run the script:**
    ```bash
    python pdf_analyzer.py
    ```

## Output

When you run the script, it will:

1.  Create a `sample.pdf` file if it doesn't already exist.
2.  Process the PDF and print its progress to the console.
3.  Generate an `analysis_results.json` file containing the results, which will look something like this:

```json
{
    "total_word_count": 41,
    "unique_word_count": 28,
    "word_frequency": {
        "this": 4,
        "is": 4,
        "the": 4,
        "page": 2,
        "document": 2,
        "a": 2,
        "simple": 2,
        "text": 2,
        "extraction": 2,
        "first": 1,
        "of": 1,
        "test": 1,
        "purpose": 1,
        "to": 1,
        "demonstrate": 1,
        "pdf": 1,
        "second": 1,
        "which": 1,
        "has": 1,
        "different": 1
    }
}
```
