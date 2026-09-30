"""
E-commerce Product Scraper
Scrapes product information (name, price, rating) from an e-commerce website
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import sys
from typing import List, Dict, Optional
from urllib.parse import urljoin


class ProductScraper:
    """Web scraper for extracting product information from e-commerce sites"""

    def __init__(self, base_url: str, max_retries: int = 3, delay: float = 1.0):
        """
        Initialize the scraper

        Args:
            base_url: Base URL of the e-commerce site
            max_retries: Maximum number of retry attempts for failed requests
            delay: Delay between requests in seconds
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self.delay = delay
        self.session = requests.Session()

        # User-Agent headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage with retry logic

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                print(f"Fetching: {url} (Attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()

                # Add delay to be respectful to the server
                time.sleep(self.delay)

                return BeautifulSoup(response.content, 'html.parser')

            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")
                if response.status_code == 404:
                    print("Page not found (404)")
                    return None

            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: {e}")

            except requests.exceptions.Timeout as e:
                print(f"Timeout Error: {e}")

            except requests.exceptions.RequestException as e:
                print(f"Request Error: {e}")

            # Wait before retrying (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

        print(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def extract_products(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract product information from a page

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of product dictionaries
        """
        products = []

        # Find all product containers
        # Note: These selectors work for https://books.toscrape.com
        # Adjust selectors based on your target website
        product_containers = soup.find_all('article', class_='product_pod')

        for container in product_containers:
            try:
                # Extract product name
                name_elem = container.find('h3').find('a')
                name = name_elem.get('title', '') if name_elem else 'N/A'

                # Extract price
                price_elem = container.find('p', class_='price_color')
                price = price_elem.text.strip() if price_elem else 'N/A'

                # Extract rating
                rating_elem = container.find('p', class_='star-rating')
                rating = rating_elem.get('class')[1] if rating_elem else 'N/A'

                products.append({
                    'name': name,
                    'price': price,
                    'rating': rating
                })

            except Exception as e:
                print(f"Error extracting product: {e}")
                continue

        return products

    def scrape_multiple_pages(self, num_pages: int = 3) -> List[Dict[str, str]]:
        """
        Scrape multiple pages of products

        Args:
            num_pages: Number of pages to scrape

        Returns:
            List of all products from all pages
        """
        all_products = []

        for page_num in range(1, num_pages + 1):
            # Construct page URL
            # Adjust this pattern based on your target website
            if page_num == 1:
                page_url = self.base_url
            else:
                page_url = urljoin(self.base_url, f'catalogue/page-{page_num}.html')

            print(f"\n{'='*60}")
            print(f"Scraping page {page_num}/{num_pages}")
            print(f"{'='*60}")

            # Fetch and parse the page
            soup = self.fetch_page(page_url)

            if soup is None:
                print(f"Skipping page {page_num} due to fetch failure")
                continue

            # Extract products from the page
            products = self.extract_products(soup)

            if products:
                print(f"Found {len(products)} products on page {page_num}")
                all_products.extend(products)
            else:
                print(f"No products found on page {page_num}")

        return all_products

    def save_to_csv(self, products: List[Dict[str, str]], filename: str = 'products.csv'):
        """
        Save products to CSV file

        Args:
            products: List of product dictionaries
            filename: Output CSV filename
        """
        if not products:
            print("No products to save")
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'price', 'rating']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(products)

            print(f"\n{'='*60}")
            print(f"Successfully saved {len(products)} products to {filename}")
            print(f"{'='*60}")

        except IOError as e:
            print(f"Error saving to CSV: {e}")
            sys.exit(1)


def main():
    """Main function to run the scraper"""

    # Example: Using books.toscrape.com (a website designed for scraping practice)
    # Replace with your target e-commerce website
    BASE_URL = 'https://books.toscrape.com/'
    NUM_PAGES = 3
    OUTPUT_FILE = 'products.csv'

    print("="*60)
    print("E-commerce Product Scraper")
    print("="*60)
    print(f"Target URL: {BASE_URL}")
    print(f"Pages to scrape: {NUM_PAGES}")
    print(f"Output file: {OUTPUT_FILE}")
    print("="*60)

    # Initialize scraper
    scraper = ProductScraper(base_url=BASE_URL, max_retries=3, delay=1.0)

    # Scrape products
    products = scraper.scrape_multiple_pages(num_pages=NUM_PAGES)

    # Save to CSV
    if products:
        scraper.save_to_csv(products, filename=OUTPUT_FILE)

        # Display sample results
        print("\nSample of scraped products (first 5):")
        print("-" * 60)
        for i, product in enumerate(products[:5], 1):
            print(f"{i}. {product['name'][:50]}...")
            print(f"   Price: {product['price']} | Rating: {product['rating']}")

        if len(products) > 5:
            print(f"\n... and {len(products) - 5} more products")
    else:
        print("\nNo products were scraped. Please check the website URL and selectors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
