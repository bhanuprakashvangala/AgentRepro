#!/usr/bin/env python3
"""Asynchronous web crawler that respects robots.txt, rate limits, and saves responses."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import aiohttp

USER_AGENT = "AsyncCrawler/1.0 (+https://example.com/bot)"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=30)


@dataclass
class CrawlResult:
    url: str
    status: Optional[int]
    path: Optional[Path]
    error: Optional[str] = None


class RobotsCache:
    """Cache robots.txt parsers keyed by netloc."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._cache: Dict[str, RobotFileParser] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def allowed(self, url: str, user_agent: str) -> bool:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        netloc = parsed.netloc
        if netloc not in self._locks:
            self._locks[netloc] = asyncio.Lock()

        async with self._locks[netloc]:
            if netloc not in self._cache:
                parser = RobotFileParser()
                robots_url = f"{parsed.scheme}://{netloc}/robots.txt"
                try:
                    async with self._session.get(robots_url) as response:
                        if response.status == 200:
                            text = await response.text()
                            parser.parse(text.splitlines())
                        else:
                            parser.parse([])
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    parser.parse([])
                self._cache[netloc] = parser

        parser = self._cache[netloc]
        return parser.can_fetch(user_agent, url)


class RateLimiter:
    """Simple per-host rate limiter enforcing minimum delay between requests."""

    def __init__(self, min_delay: float) -> None:
        self._min_delay = min_delay
        self._last_access: Dict[str, float] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def wait(self, host: str) -> None:
        if host not in self._locks:
            self._locks[host] = asyncio.Lock()
        async with self._locks[host]:
            now = time.monotonic()
            last = self._last_access.get(host)
            if last is not None:
                elapsed = now - last
                if elapsed < self._min_delay:
                    await asyncio.sleep(self._min_delay - elapsed)
            self._last_access[host] = time.monotonic()


async def fetch_url(
    session: aiohttp.ClientSession,
    robots: RobotsCache,
    rate_limiter: RateLimiter,
    output_dir: Path,
    url: str,
) -> CrawlResult:
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        return CrawlResult(url=url, status=None, path=None, error="Unsupported scheme")

    allowed = await robots.allowed(url, USER_AGENT)
    if not allowed:
        return CrawlResult(url=url, status=None, path=None, error="Blocked by robots.txt")

    await rate_limiter.wait(parsed.netloc)

    try:
        async with session.get(url) as response:
            status = response.status
            if status != 200:
                return CrawlResult(url=url, status=status, path=None, error=f"HTTP {status}")

            content = await response.read()
            output_dir.mkdir(parents=True, exist_ok=True)
            filename = hashlib.sha256(url.encode()).hexdigest() + ".html"
            path = output_dir / filename
            path.write_bytes(content)
            return CrawlResult(url=url, status=status, path=path)
    except asyncio.TimeoutError:
        return CrawlResult(url=url, status=None, path=None, error="Timeout")
    except aiohttp.ClientError as exc:
        return CrawlResult(url=url, status=None, path=None, error=str(exc))


async def crawl_urls(urls: Iterable[str], output_dir: Path, concurrency: int, min_delay: float) -> List[CrawlResult]:
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    async with aiohttp.ClientSession(
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
        connector=connector,
    ) as session:
        robots = RobotsCache(session)
        rate_limiter = RateLimiter(min_delay)
        semaphore = asyncio.Semaphore(concurrency)

        async def worker(url: str) -> CrawlResult:
            async with semaphore:
                return await fetch_url(session, robots, rate_limiter, output_dir, url)

        tasks = [asyncio.create_task(worker(url)) for url in urls]
        results = await asyncio.gather(*tasks)
    return results


def parse_input_urls(args: argparse.Namespace) -> List[str]:
    urls: List[str] = []
    if args.urls_file:
        file_path = Path(args.urls_file)
        if not file_path.exists():
            raise FileNotFoundError(f"URLs file not found: {file_path}")
        urls.extend([line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    if args.url:
        urls.extend(args.url)
    urls = [u for u in urls if u]
    if not urls:
        raise ValueError("No URLs provided. Use --url or --urls-file.")
    return urls


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Asynchronous web crawler with robots.txt compliance")
    parser.add_argument("--url", action="append", help="URL to crawl (can be specified multiple times)")
    parser.add_argument("--urls-file", help="Path to a file containing URLs (one per line)")
    parser.add_argument("--output-dir", default="crawled", help="Directory to store downloaded content")
    parser.add_argument("--concurrency", type=int, default=5, help="Maximum number of concurrent requests")
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Minimum delay in seconds between requests to the same host",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        urls = parse_input_urls(args)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir).resolve()
    concurrency = max(1, args.concurrency)
    try:
        results = asyncio.run(crawl_urls(urls, output_dir, concurrency, max(0.0, args.delay)))
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        sys.exit(1)

    success = 0
    for result in results:
        if result.error:
            print(f"FAIL {result.url} :: {result.error}")
        else:
            success += 1
            output = result.path.resolve() if result.path else None
            print(f"OK   {result.url} -> {output}")

    print(f"Crawl finished. {success}/{len(results)} succeeded.")


if __name__ == "__main__":
    main()
