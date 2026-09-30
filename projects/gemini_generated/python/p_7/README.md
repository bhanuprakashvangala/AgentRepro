# Async Web Crawler

This project is a simple asynchronous web crawler built with Python's `asyncio` and `aiohttp` libraries. It is designed to crawl multiple websites concurrently while being mindful of rate limits.

## Features

- **Asynchronous Crawling**: Uses `aiohttp` to fetch multiple URLs concurrently.
- **Rate Limiting**: Includes a simple delay mechanism to avoid sending too many requests to the same server in a short period.
- **Content Saving**: Saves the HTML content of each crawled page into the `crawled_content` directory.
- **Responsible User-Agent**: Sets a clear User-Agent string.

*Note: For simplicity, this example does not include a `robots.txt` parser. In a real-world scenario, you should use a library like `aiohttp-robotparser` to ensure you respect the website's crawling policies before fetching any URL.*

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

3.  **Run the crawler:**
    ```bash
    python async_crawler.py
    ```

## Output

When you run the script, it will:

1.  Create a directory named `crawled_content` if it doesn't exist.
2.  Crawl the list of predefined URLs (`quotes.toscrape.com` and `books.toscrape.com`).
3.  Save the HTML content of each page as a separate file inside the `crawled_content` directory.

The script will print its progress to the console, indicating which URLs are being crawled and where the content is being saved.
