# Sentiment Analysis Tool

This Python script analyzes customer reviews from a CSV file and classifies them as positive, negative, or neutral using the TextBlob library.

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

3.  **Download TextBlob corpora:**
    ```bash
    python -m textblob.download_corpora
    ```

4.  **Run the sentiment analyzer:**
    ```bash
    python sentiment_analyzer.py
    ```

    This will:
    *   Read reviews from `sample_reviews.csv`.
    *   Generate a `sentiment_report.csv` file with the analysis for each review.
    *   Print a summary report to the console.
