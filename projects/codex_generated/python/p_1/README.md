# Python Product Scraper

This script uses `requests` and `beautifulsoup4` to scrape product data (name, price, rating) from an e-commerce catalog such as [Books to Scrape](https://books.toscrape.com/). Results are written to a CSV file while gracefully handling pagination and transient network errors.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py --pages 3 --output products.csv
```

Options:
- `--pages`: Number of catalog pages to visit (minimum 3).
- `--output`: CSV file destination (defaults to `products.csv`).
- `--base-url`: Optional URL template containing `{page}` (defaults to the Books to Scrape catalog).
- `--delay`: Seconds to wait between requests (defaults to 1 second).

The script automatically adds a desktop browser user-agent header and retries failed requests up to 3 times before skipping a page.

## Output

The resulting CSV contains three columns: `name`, `price`, and `rating`.
