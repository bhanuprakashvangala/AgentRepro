# Plagiarism Detector

Compares text documents using `difflib.SequenceMatcher`, calculates similarity percentages, and generates HTML reports highlighting matching segments.

## Setup
(Optional virtualenv)
```bash
python3 -m venv .venv
source .venv/bin/activate
```
(No external dependencies required.)

## Usage
```bash
python plagiarism_detector.py --inputs docs/*.txt --output-dir reports --min-match-length 40
```

Outputs:
- `reports/summary.csv` – Similarity percentages between each pair.
- `reports/<docA>_vs_<docB>.html` – Highlighted comparisons showing matching spans.

Adjust `--min-match-length` to control highlighted block size (characters). The tool ignores missing files and proceeds with comparisons for available documents.
