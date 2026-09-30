# E-commerce Web Scraper

This Python script scrapes product information (name, price, and rating) from the website [books.toscrape.com](http://books.toscrape.com).

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

3.  **Run the scraper:**
    ```bash
    python scraper.py
    ```

    This will create a `products.csv` file in the same directory with the scraped data.
