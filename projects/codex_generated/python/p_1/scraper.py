#!/usr/bin/env python3
"""Scrape product information from an e-commerce catalog."""

import argparse
import csv
import sys
import time
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_BASE_URL = "https://books.toscrape.com/catalogue/page-{page}.html"


@dataclass
class Product:
    name: str
    price: str
    rating: str


def fetch_with_retries(url: str, session: requests.Session, retries: int = 3, backoff: float = 1.0) -> str:
    """Fetch URL contents with retry handling for transient network failures."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            if attempt == retries:
                print(f"Failed to fetch {url}: {exc}", file=sys.stderr)
                return ""
            wait_time = backoff * attempt
            print(
                f"Error fetching {url} (attempt {attempt}/{retries}). Retrying in {wait_time:.1f}s...",
                file=sys.stderr,
            )
            time.sleep(wait_time)
    return ""


def parse_products(html: str) -> List[Product]:
    """Parse product information (name, price, rating) from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    products: List[Product] = []

    for article in soup.select("article.product_pod"):
        title_tag = article.select_one("h3 a")
        price_tag = article.select_one("p.price_color")
        rating_tag = article.select_one("p.star-rating")

        if not (title_tag and price_tag and rating_tag):
            continue

        rating_classes = rating_tag.get("class", [])
        rating_value = next((cls for cls in rating_classes if cls != "star-rating"), "N/A")

        products.append(
            Product(
                name=title_tag.get("title") or title_tag.get_text(strip=True),
                price=price_tag.get_text(strip=True),
                rating=rating_value,
            )
        )

    return products


def scrape_products(base_url_template: str, pages: int, delay: float) -> List[Product]:
    """Scrape multiple catalog pages and return collected products."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        }
    )

    all_products: List[Product] = []
    for page in range(1, pages + 1):
        url = base_url_template.format(page=page, page_number=page)
        html = fetch_with_retries(url, session)
        if not html:
            continue

        products = parse_products(html)
        print(f"Page {page}: found {len(products)} products")
        all_products.extend(products)

        if page != pages and delay > 0:
            time.sleep(delay)

    return all_products


def save_to_csv(products: List[Product], path: str) -> None:
    """Save products to CSV file."""
    fieldnames = ["name", "price", "rating"]
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products:
            writer.writerow(
                {
                    "name": product.name,
                    "price": product.price,
                    "rating": product.rating,
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape product details (name, price, rating) from an e-commerce listing."
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Number of catalog pages to scrape (minimum 3).",
    )
    parser.add_argument(
        "--output",
        default="products.csv",
        help="Output CSV file path.",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL template containing {page} or {page_number} placeholder.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between page requests.",
    )
    args = parser.parse_args()

    if args.pages < 3:
        parser.error("--pages must be at least 3.")

    if "{page}" not in args.base_url and "{page_number}" not in args.base_url:
        parser.error("--base-url must contain either '{page}' or '{page_number}'.")

    return args


def main() -> None:
    args = parse_args()

    base_url_template = args.base_url.replace("{page_number}", "{page}")
    products = scrape_products(base_url_template, args.pages, args.delay)

    if not products:
        print("No products scraped. Please verify the base URL or try again later.", file=sys.stderr)
        sys.exit(1)

    save_to_csv(products, args.output)
    print(f"Saved {len(products)} products to {args.output}")


if __name__ == "__main__":
    main()
