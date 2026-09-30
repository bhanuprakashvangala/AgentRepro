import asyncio
import aiohttp
import aiofiles
import os
from urllib.parse import urlparse, urljoin
import time
from collections import defaultdict
import re

# It's good practice to use a dedicated robot parser library, 
# but for a self-contained script, a simple manual check is sufficient for this example.
# For a real-world crawler, consider `aiohttp-robotparser`.

# --- Configuration ---
USER_AGENT = "Gemini-Reproducible-Crawler/1.0 (https://example.com/bot-info)"
# Delay between requests to the same domain in seconds
RATE_LIMIT_DELAY = 1.0 
OUTPUT_DIR = "crawled_content"

class AsyncCrawler:
    def __init__(self, start_urls):
        self.start_urls = start_urls
        self.session = None
        self.last_request_times = defaultdict(float)
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    async def rate_limit(self, domain):
        """Enforces a delay between requests to the same domain."""
        now = time.time()
        last_request_time = self.last_request_times[domain]
        elapsed = now - last_request_time

        if elapsed < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - elapsed
            print(f"Rate limiting {domain}. Sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        self.last_request_times[domain] = time.time()

    async def fetch(self, url):
        """Fetches a single URL, respecting rate limits."""
        domain = urlparse(url).netloc
        await self.rate_limit(domain)
        
        print(f"Crawling: {url}")
        headers = {"User-Agent": USER_AGENT}
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            print(f"Error fetching {url}: {e}")
        except asyncio.TimeoutError:
            print(f"Timeout error fetching {url}")
        return None

    async def save_content(self, url, content):
        """Saves the fetched content to a file."""
        # Sanitize URL to create a valid filename
        filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', url) + '.html'
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(content)
            print(f"Saved content from {url} to {filepath}")
        except IOError as e:
            print(f"Error saving file for {url}: {e}")

    async def crawl_url(self, url):
        """The main workflow for crawling a single URL."""
        # In a real crawler, you would check robots.txt here.
        # For this example, we assume we are allowed to crawl the given URLs.
        content = await self.fetch(url)
        if content:
            await self.save_content(url, content)

    async def run(self):
        """Runs the crawler for the given start URLs."""
        async with aiohttp.ClientSession() as session:
            self.session = session
            tasks = [self.crawl_url(url) for url in self.start_urls]
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Use websites designed for scraping to ensure reproducibility and avoid issues.
    # These sites have permissive or non-existent robots.txt files.
    urls_to_crawl = [
        "http://quotes.toscrape.com/",
        "http://books.toscrape.com/",
        "http://quotes.toscrape.com/page/2/",
    ]
    
    print("--- Starting Async Web Crawler ---")
    crawler = AsyncCrawler(urls_to_crawl)
    asyncio.run(crawler.run())
    print("\n--- Crawler Finished ---")
