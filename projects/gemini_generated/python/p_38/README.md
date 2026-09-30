# Plagiarism Detector for Text Documents

This is a command-line tool that detects potential plagiarism by comparing a source text document against one or more comparison documents. It works by analyzing the similarity between individual sentences.

## Features

- **Sentence-Level Comparison**: Instead of just comparing whole files, the tool breaks down documents into sentences and compares them individually for more granular analysis.
- **Similarity Scoring**: Uses Python's `difflib.SequenceMatcher` to calculate a similarity ratio for each pair of sentences.
- **Detailed Reporting**: For each comparison, it generates a `.txt` report that includes:
    - An overall similarity score (percentage of matching sentences).
    - A "highlighted" list of all sentence pairs that exceed the similarity threshold.
- **Reproducible Demo**: Includes a `--demo` mode that automatically generates a set of sample documents and runs the analysis, making it easy to test and understand the tool's functionality.
- **Automatic Setup**: On the first run, the script automatically downloads the necessary `punkt` tokenizer data from `nltk`.

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
    This is the best way to see the tool in action. It will create a `demo_texts/` directory with sample files and generate reports for them.
    ```bash
    python plagiarism_detector.py --demo
    ```

4.  **Check Your Own Files:**
    Provide a source file followed by one or more files to compare it against.

    ```bash
    # Compare my_paper.txt against two other sources
    python plagiarism_detector.py my_paper.txt source1.txt source2.txt

    # Adjust the similarity threshold to 70%
    python plagiarism_detector.py my_paper.txt source1.txt --threshold 0.7
    ```

## Output

For each comparison (e.g., `source.txt` vs. `original1.txt`), a report file (e.g., `report_source.txt_vs_original1.txt.txt`) will be created. This report will contain the analysis, including the highlighted matching sections.
