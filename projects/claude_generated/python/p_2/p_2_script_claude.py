"""
Sentiment Analysis Tool for Customer Reviews
Analyzes CSV files containing customer reviews and generates sentiment reports.
"""

import pandas as pd
from textblob import TextBlob
import sys
from pathlib import Path
from datetime import datetime
import json


class SentimentAnalyzer:
    """Analyzes sentiment of customer reviews using TextBlob."""

    def __init__(self):
        self.results = []

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single review.

        Returns:
            dict: Contains sentiment label, polarity score, and confidence
        """
        if pd.isna(text) or not isinstance(text, str) or len(text.strip()) == 0:
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'confidence': 0.0
            }

        try:
            blob = TextBlob(str(text))
            polarity = blob.sentiment.polarity

            # Calculate confidence based on absolute polarity value
            # Higher absolute values indicate stronger sentiment
            confidence = abs(polarity)

            # Classify sentiment based on polarity
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 4),
                'confidence': round(confidence, 4)
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'confidence': 0.0
            }

    def process_csv(self, input_file, review_column='review', output_file=None):
        """
        Process a CSV file containing customer reviews.

        Args:
            input_file: Path to input CSV file
            review_column: Name of the column containing reviews
            output_file: Path to output CSV file (optional)

        Returns:
            pandas.DataFrame: DataFrame with sentiment analysis results
        """
        print(f"Loading reviews from {input_file}...")

        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            sys.exit(1)

        if review_column not in df.columns:
            print(f"Error: Column '{review_column}' not found in CSV.")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)

        print(f"Analyzing {len(df)} reviews...")

        # Analyze each review
        results = df[review_column].apply(self.analyze_sentiment)

        # Extract sentiment components into separate columns
        df['sentiment'] = results.apply(lambda x: x['sentiment'])
        df['polarity_score'] = results.apply(lambda x: x['polarity'])
        df['confidence_score'] = results.apply(lambda x: x['confidence'])

        # Save results if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")

        self.results = df
        return df

    def generate_report(self, save_to_file=None):
        """
        Generate a statistical report of sentiment analysis results.

        Args:
            save_to_file: Optional path to save report as text file

        Returns:
            str: Formatted report string
        """
        if self.results is None or len(self.results) == 0:
            return "No results to generate report from."

        df = self.results
        total_reviews = len(df)

        # Count sentiments
        sentiment_counts = df['sentiment'].value_counts()
        positive_count = sentiment_counts.get('positive', 0)
        negative_count = sentiment_counts.get('negative', 0)
        neutral_count = sentiment_counts.get('neutral', 0)

        # Calculate percentages
        positive_pct = (positive_count / total_reviews) * 100
        negative_pct = (negative_count / total_reviews) * 100
        neutral_pct = (neutral_count / total_reviews) * 100

        # Calculate average scores
        avg_polarity = df['polarity_score'].mean()
        avg_confidence = df['confidence_score'].mean()

        # Get most positive and negative reviews
        most_positive = df.nlargest(3, 'polarity_score')
        most_negative = df.nsmallest(3, 'polarity_score')

        # Build report
        report = []
        report.append("=" * 70)
        report.append("SENTIMENT ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Reviews Analyzed: {total_reviews}")
        report.append("")

        report.append("-" * 70)
        report.append("OVERALL SENTIMENT DISTRIBUTION")
        report.append("-" * 70)
        report.append(f"Positive: {positive_count:>6} ({positive_pct:>5.1f}%)")
        report.append(f"Neutral:  {neutral_count:>6} ({neutral_pct:>5.1f}%)")
        report.append(f"Negative: {negative_count:>6} ({negative_pct:>5.1f}%)")
        report.append("")

        report.append("-" * 70)
        report.append("STATISTICAL SUMMARY")
        report.append("-" * 70)
        report.append(f"Average Polarity Score: {avg_polarity:.4f}")
        report.append(f"  (Range: -1.0 to +1.0, where -1 is most negative, +1 is most positive)")
        report.append(f"Average Confidence Score: {avg_confidence:.4f}")
        report.append(f"  (Range: 0.0 to 1.0, higher values indicate stronger sentiment)")
        report.append("")

        # Polarity distribution
        report.append("-" * 70)
        report.append("POLARITY SCORE DISTRIBUTION")
        report.append("-" * 70)
        report.append(f"Minimum: {df['polarity_score'].min():.4f}")
        report.append(f"25th Percentile: {df['polarity_score'].quantile(0.25):.4f}")
        report.append(f"Median: {df['polarity_score'].median():.4f}")
        report.append(f"75th Percentile: {df['polarity_score'].quantile(0.75):.4f}")
        report.append(f"Maximum: {df['polarity_score'].max():.4f}")
        report.append("")

        # Most positive reviews
        if len(most_positive) > 0:
            report.append("-" * 70)
            report.append("TOP 3 MOST POSITIVE REVIEWS")
            report.append("-" * 70)
            for idx, row in most_positive.iterrows():
                review_col = [col for col in df.columns if col not in
                            ['sentiment', 'polarity_score', 'confidence_score']][0]
                review_text = str(row[review_col])[:150]
                report.append(f"Polarity: {row['polarity_score']:.4f} | Confidence: {row['confidence_score']:.4f}")
                report.append(f"Review: {review_text}...")
                report.append("")

        # Most negative reviews
        if len(most_negative) > 0:
            report.append("-" * 70)
            report.append("TOP 3 MOST NEGATIVE REVIEWS")
            report.append("-" * 70)
            for idx, row in most_negative.iterrows():
                review_col = [col for col in df.columns if col not in
                            ['sentiment', 'polarity_score', 'confidence_score']][0]
                review_text = str(row[review_col])[:150]
                report.append(f"Polarity: {row['polarity_score']:.4f} | Confidence: {row['confidence_score']:.4f}")
                report.append(f"Review: {review_text}...")
                report.append("")

        report.append("=" * 70)

        report_text = "\n".join(report)

        # Save to file if requested
        if save_to_file:
            with open(save_to_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"Report saved to {save_to_file}")

        return report_text


def main():
    """Main function to run sentiment analysis from command line."""

    if len(sys.argv) < 2:
        print("Usage: python sentiment_analyzer.py <input_csv> [review_column] [output_csv]")
        print("\nExample: python sentiment_analyzer.py reviews.csv review results.csv")
        print("\nArguments:")
        print("  input_csv      : Path to CSV file containing reviews (required)")
        print("  review_column  : Name of column containing review text (default: 'review')")
        print("  output_csv     : Path to save results CSV (default: 'sentiment_results.csv')")
        sys.exit(1)

    input_file = sys.argv[1]
    review_column = sys.argv[2] if len(sys.argv) > 2 else 'review'
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'sentiment_results.csv'

    # Initialize analyzer
    analyzer = SentimentAnalyzer()

    # Process CSV
    results = analyzer.process_csv(input_file, review_column, output_file)

    # Generate and display report
    report = analyzer.generate_report(save_to_file='sentiment_report.txt')
    print("\n" + report)


if __name__ == "__main__":
    main()
