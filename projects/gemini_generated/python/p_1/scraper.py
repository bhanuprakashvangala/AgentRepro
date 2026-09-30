import requests
from bs4 import BeautifulSoup
import csv

def scrape_books(num_pages=3):
    """
    Scrapes book information (name, price, rating) from books.toscrape.com.

    Args:
        num_pages (int): The number of pages to scrape.

    Returns:
        list: A list of lists containing the scraped book data.
    """
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    all_books = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for page in range(1, num_pages + 1):
        url = base_url.format(page)
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for bad status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        for book in books:
            name = book.h3.a["title"]
            price = book.find("p", class_="price_color").text
            rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
            rating_class = book.find("p", class_="star-rating")["class"]
            rating = rating_map.get(rating_class[1], 0)
            all_books.append([name, price, rating])

    return all_books

def save_to_csv(data, filename="products.csv"):
    """
    Saves data to a CSV file.

    Args:
        data (list): The data to save.
        filename (str): The name of the CSV file.
    """
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Name", "Price", "Rating"])
        writer.writerows(data)

if __name__ == "__main__":
    scraped_data = scrape_books(num_pages=3)
    if scraped_data:
        save_to_csv(scraped_data)
        print(f"Scraped {len(scraped_data)} products and saved to products.csv")
