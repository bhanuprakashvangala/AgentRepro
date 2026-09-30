# Puppeteer Web Scraper

Headless scraper using Puppeteer to extract JS-rendered content across multiple pages.

## Setup
```bash
npm install
```

## Usage
Set target site (must provide `.listing-card`/`.result-item` selectors) and optional page count:
```bash
TARGET_URL="https://example.com/listings" MAX_PAGES=5 npm start
```

Outputs `results.json` with scraped data:
```json
{
  "scrapedAt": "2023-10-29T12:00:00.000Z",
  "data": [
    { "title": "Item", "price": "$99", "link": "https://...", "description": "..." }
  ]
}
```

Modify DOM selectors inside `scrape.js` to match your target site structure.
