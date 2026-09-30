"""
Async Web Crawler with robots.txt support, rate limiting, and concurrent crawling.
"""
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from typing import Set, Dict, List
from pathlib import Path
from datetime import datetime
import time
import hashlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter to control request frequency per domain."""

    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time: Dict[str, float] = {}
        self.locks: Dict[str, asyncio.Lock] = {}

    async def wait(self, domain: str):
        """Wait if necessary to respect rate limit for domain."""
        if domain not in self.locks:
            self.locks[domain] = asyncio.Lock()

        async with self.locks[domain]:
            current_time = time.time()
            last_time = self.last_request_time.get(domain, 0)
            time_since_last = current_time - last_time

            if time_since_last < self.min_interval:
                wait_time = self.min_interval - time_since_last
                logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            self.last_request_time[domain] = time.time()


class RobotsTxtChecker:
    """Check and cache robots.txt rules for domains."""

    def __init__(self):
        self.parsers: Dict[str, RobotFileParser] = {}
        self.user_agent = "AsyncWebCrawler/1.0"

    async def can_fetch(self, session: ClientSession, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self.parsers:
            await self._load_robots_txt(session, domain)

        parser = self.parsers.get(domain)
        if parser is None:
            # If robots.txt couldn't be loaded, allow crawling
            return True

        return parser.can_fetch(self.user_agent, url)

    async def _load_robots_txt(self, session: ClientSession, domain: str):
        """Load and parse robots.txt for a domain."""
        robots_url = f"{domain}/robots.txt"
        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            async with session.get(robots_url, timeout=ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    parser.parse(content.splitlines())
                    logger.info(f"Loaded robots.txt for {domain}")
                else:
                    logger.warning(f"No robots.txt found for {domain} (status {response.status})")
                    parser = None
        except Exception as e:
            logger.warning(f"Error loading robots.txt for {domain}: {e}")
            parser = None

        self.parsers[domain] = parser


class AsyncWebCrawler:
    """Async web crawler with concurrent crawling capabilities."""

    def __init__(
        self,
        max_concurrent_requests: int = 5,
        requests_per_second: float = 2.0,
        max_depth: int = 2,
        output_dir: str = "crawled_data"
    ):
        self.max_concurrent_requests = max_concurrent_requests
        self.max_depth = max_depth
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.rate_limiter = RateLimiter(requests_per_second)
        self.robots_checker = RobotsTxtChecker()

        self.visited_urls: Set[str] = set()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        self.headers = {
            'User-Agent': 'AsyncWebCrawler/1.0 (+https://example.com/bot)'
        }

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def _url_to_filename(self, url: str) -> str:
        """Convert URL to safe filename."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '_')
        return f"{domain}_{url_hash}.html"

    async def fetch_url(self, session: ClientSession, url: str) -> tuple[str, str]:
        """Fetch a single URL with rate limiting and robots.txt check."""
        domain = self._get_domain(url)

        # Check robots.txt
        if not await self.robots_checker.can_fetch(session, url):
            logger.warning(f"Blocked by robots.txt: {url}")
            return url, None

        # Apply rate limiting
        await self.rate_limiter.wait(domain)

        async with self.semaphore:
            try:
                logger.info(f"Fetching: {url}")
                async with session.get(
                    url,
                    headers=self.headers,
                    timeout=ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.info(f"Successfully fetched {url} ({len(content)} bytes)")
                        return url, content
                    else:
                        logger.warning(f"Failed to fetch {url}: status {response.status}")
                        return url, None
            except asyncio.TimeoutError:
                logger.error(f"Timeout fetching {url}")
                return url, None
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return url, None

    def save_content(self, url: str, content: str):
        """Save crawled content to file."""
        if content is None:
            return

        filename = self._url_to_filename(url)
        filepath = self.output_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<!-- URL: {url} -->\n")
                f.write(f"<!-- Crawled at: {datetime.now().isoformat()} -->\n\n")
                f.write(content)
            logger.info(f"Saved content to {filepath}")
        except Exception as e:
            logger.error(f"Error saving content for {url}: {e}")

    def extract_links(self, base_url: str, html_content: str) -> List[str]:
        """Extract links from HTML content (basic implementation)."""
        if html_content is None:
            return []

        # Simple link extraction (for production, use BeautifulSoup or lxml)
        import re
        links = []

        # Find href attributes
        href_pattern = r'href=["\'](.*?)["\']'
        matches = re.findall(href_pattern, html_content, re.IGNORECASE)

        for match in matches:
            # Skip anchors, javascript, and mailto links
            if match.startswith('#') or match.startswith('javascript:') or match.startswith('mailto:'):
                continue

            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, match)

            # Only keep HTTP(S) URLs
            if absolute_url.startswith('http'):
                links.append(absolute_url)

        return links

    async def crawl_url(
        self,
        session: ClientSession,
        url: str,
        depth: int = 0
    ):
        """Recursively crawl a URL and its links."""
        if depth > self.max_depth or url in self.visited_urls:
            return

        self.visited_urls.add(url)

        # Fetch the URL
        url, content = await self.fetch_url(session, url)

        if content:
            # Save the content
            self.save_content(url, content)

            # Extract and crawl links if we haven't reached max depth
            if depth < self.max_depth:
                links = self.extract_links(url, content)
                logger.info(f"Found {len(links)} links on {url}")

                # Crawl links concurrently
                tasks = []
                for link in links:
                    if link not in self.visited_urls:
                        tasks.append(self.crawl_url(session, link, depth + 1))

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

    async def crawl(self, urls: List[str]):
        """Crawl multiple URLs concurrently."""
        logger.info(f"Starting crawl of {len(urls)} URLs")
        logger.info(f"Max depth: {self.max_depth}, Max concurrent requests: {self.max_concurrent_requests}")

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_url(session, url) for url in urls]
            await asyncio.gather(*tasks, return_exceptions=True)

        elapsed_time = time.time() - start_time
        logger.info(f"Crawl completed in {elapsed_time:.2f} seconds")
        logger.info(f"Total URLs visited: {len(self.visited_urls)}")
        logger.info(f"Content saved to: {self.output_dir.absolute()}")


async def main():
    """Example usage of the async web crawler."""
    # Example URLs to crawl
    urls_to_crawl = [
        "http://example.com",
        "http://httpbin.org/html",
        # Add more URLs here
    ]

    crawler = AsyncWebCrawler(
        max_concurrent_requests=5,  # Maximum concurrent requests
        requests_per_second=2.0,    # Requests per second per domain
        max_depth=2,                 # Maximum crawl depth
        output_dir="crawled_data"    # Output directory
    )

    await crawler.crawl(urls_to_crawl)


if __name__ == "__main__":
    asyncio.run(main())
