# Async Web Crawler

This tool crawls multiple URLs concurrently using `asyncio` and `aiohttp`. It respects `robots.txt`, enforces a per-host delay, and writes downloaded content to disk.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python async_crawler.py --url https://example.com --url https://example.org --output-dir crawled --concurrency 5 --delay 1.5
```

You can also provide a text file of URLs (one per line):

```bash
python async_crawler.py --urls-file urls.txt --output-dir crawled
```

Options:
- `--url`: Specify URLs directly (repeatable).
- `--urls-file`: Text file containing URLs.
- `--output-dir`: Directory where responses are saved (default `crawled`).
- `--concurrency`: Maximum simultaneous requests (default `5`).
- `--delay`: Minimum delay between requests to the same host in seconds (default `1.0`).

Saved files are named by the SHA-256 hash of their URL with a `.html` extension. The crawler logs successes and failures to stdout/stderr and aborts politely on `Ctrl+C`.
