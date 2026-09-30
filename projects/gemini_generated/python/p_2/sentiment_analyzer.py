from textblob import TextBlob
import csv

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text.

    Args:
        text (str): The text to analyze.

    Returns:
        tuple: A tuple containing the sentiment (Positive, Negative, Neutral)
               and the confidence score (polarity).
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, abs(polarity)

def process_reviews(input_file, output_file):
    """
    Processes a CSV file of reviews, analyzes sentiment, and saves the results.

    Args:
        input_file (str): The path to the input CSV file.
        output_file (str): The path to the output CSV file.
    """
    reviews = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            reviews.append(row['review_text'])

    results = []
    for review in reviews:
        sentiment, confidence = analyze_sentiment(review)
        results.append({'review': review, 'sentiment': sentiment, 'confidence': confidence})

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['review', 'sentiment', 'confidence'])
        writer.writeheader()
        writer.writerows(results)

    generate_report(results)

def generate_report(results):
    """
    Generates a sentiment analysis report.

    Args:
        results (list): A list of dictionaries containing the analysis results.
    """
    total_reviews = len(results)
    positive_count = sum(1 for r in results if r['sentiment'] == 'Positive')
    negative_count = sum(1 for r in results if r['sentiment'] == 'Negative')
    neutral_count = sum(1 for r in results if r['sentiment'] == 'Neutral')

    print("--- Sentiment Analysis Report ---")
    print(f"Total Reviews Analyzed: {total_reviews}")
    print(f"Positive Reviews: {positive_count} ({positive_count/total_reviews:.2%})")
    print(f"Negative Reviews: {negative_count} ({negative_count/total_reviews:.2%})")
    print(f"Neutral Reviews: {neutral_count} ({neutral_count/total_reviews:.2%})")
    print("---------------------------------")

if __name__ == "__main__":
    input_csv = "sample_reviews.csv"
    output_csv = "sentiment_report.csv"
    process_reviews(input_csv, output_csv)
    print(f"Sentiment analysis complete. Report saved to {output_csv}")
