# Sentiment Analysis Tool

This utility classifies customer reviews as positive, negative, or neutral using TextBlob. It reads reviews from a CSV file, annotates each entry with sentiment scores, and produces a summary report with useful statistics.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Prepare a CSV file that contains a `review` column (or pass `--text-column` for a different name). Then run:

```bash
python sentiment_analyzer.py --input reviews.csv --output sentiment_results.csv --report sentiment_report.json
```

Key options:
- `--input`: Path to the CSV file containing reviews (required).
- `--text-column`: Column name with review text (default: `review`).
- `--threshold`: Polarity cutoff for positive/negative classification (default: `0.1`).
- `--output`: CSV file storing per-review sentiment, polarity, subjectivity, and confidence.
- `--report`: JSON file summarizing counts and average metrics.

The script prints the aggregated report to stdout and writes:
1. `sentiment_results.csv` — individual sentiment annotations.
2. `sentiment_report.json` — statistics including label distribution and average scores.
