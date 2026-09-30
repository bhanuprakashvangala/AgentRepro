# PDF Text Extraction & Analysis

This script extracts text from PDF documents using `pdfplumber`, performs simple NLP counts, and exports the results in JSON or CSV format.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Analyze a single PDF
```bash
python extractor.py --input document.pdf --output analysis.json
```

### Analyze all PDFs in a directory
```bash
python extractor.py --input ./pdfs --output report.csv --limit-pages 5
```

Options:
- `--input`: PDF file or directory of PDFs to analyze (required).
- `--output`: Destination file (`.json` or `.csv` determines format; default `analysis.json`).
- `--limit-pages`: Optional cap on number of pages processed per PDF.

The output includes per-file word count, unique word count, character count, and the top 20 most frequent tokens. CSV exports the top words as a semicolon-separated list (`word:count`).
