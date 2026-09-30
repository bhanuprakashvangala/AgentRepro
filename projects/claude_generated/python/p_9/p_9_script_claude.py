"""
PDF Text Extraction and Analysis Tool
Extracts text from PDF files and performs NLP analysis
"""

import json
import csv
from pathlib import Path
from collections import Counter
import re
from typing import Dict, List, Tuple

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Run: pip install pdfplumber")
    exit(1)


class PDFAnalyzer:
    """Extract and analyze text from PDF documents"""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.text_by_page = []
        self.full_text = ""
        self.analysis_results = {}

    def extract_text(self) -> bool:
        """Extract text from all pages of the PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Processing PDF: {self.pdf_path.name}")
                print(f"Total pages: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        self.text_by_page.append({
                            'page': page_num,
                            'text': text,
                            'char_count': len(text)
                        })
                        self.full_text += text + "\n"
                    else:
                        print(f"Warning: No text found on page {page_num}")

                return True

        except FileNotFoundError:
            print(f"Error: PDF file not found: {self.pdf_path}")
            return False
        except Exception as e:
            print(f"Error extracting text: {e}")
            return False

    def analyze_text(self) -> Dict:
        """Perform NLP analysis on extracted text"""
        if not self.full_text:
            print("No text to analyze. Extract text first.")
            return {}

        # Clean and tokenize text
        words = self._tokenize(self.full_text)

        # Basic statistics
        total_chars = len(self.full_text)
        total_words = len(words)
        unique_words = len(set(words))

        # Word frequency analysis
        word_freq = Counter(words)
        top_words = word_freq.most_common(20)

        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0

        # Sentence count (simple estimation)
        sentences = re.split(r'[.!?]+', self.full_text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Store results
        self.analysis_results = {
            'file_name': self.pdf_path.name,
            'total_pages': len(self.text_by_page),
            'total_characters': total_chars,
            'total_words': total_words,
            'unique_words': unique_words,
            'average_word_length': round(avg_word_length, 2),
            'estimated_sentences': sentence_count,
            'lexical_diversity': round(unique_words / total_words, 4) if total_words > 0 else 0,
            'top_20_words': [{'word': word, 'count': count} for word, count in top_words],
            'pages_analysis': [
                {
                    'page': p['page'],
                    'character_count': p['char_count'],
                    'word_count': len(self._tokenize(p['text']))
                }
                for p in self.text_by_page
            ]
        }

        return self.analysis_results

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words (lowercase, alphanumeric only)"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        # Filter out very short words (optional)
        return [w for w in words if len(w) > 1]

    def export_to_json(self, output_path: str = None):
        """Export analysis results to JSON file"""
        if not self.analysis_results:
            print("No analysis results to export. Run analyze_text() first.")
            return

        if output_path is None:
            output_path = self.pdf_path.stem + "_analysis.json"

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON results exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")

    def export_to_csv(self, output_path: str = None):
        """Export word frequency results to CSV file"""
        if not self.analysis_results:
            print("No analysis results to export. Run analyze_text() first.")
            return

        if output_path is None:
            output_path = self.pdf_path.stem + "_word_frequency.csv"

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Write summary statistics
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['File Name', self.analysis_results['file_name']])
                writer.writerow(['Total Pages', self.analysis_results['total_pages']])
                writer.writerow(['Total Words', self.analysis_results['total_words']])
                writer.writerow(['Unique Words', self.analysis_results['unique_words']])
                writer.writerow(['Average Word Length', self.analysis_results['average_word_length']])
                writer.writerow(['Lexical Diversity', self.analysis_results['lexical_diversity']])
                writer.writerow([])

                # Write word frequency table
                writer.writerow(['Rank', 'Word', 'Frequency'])
                for rank, word_data in enumerate(self.analysis_results['top_20_words'], 1):
                    writer.writerow([rank, word_data['word'], word_data['count']])

            print(f"✓ CSV results exported to: {output_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")

    def print_summary(self):
        """Print analysis summary to console"""
        if not self.analysis_results:
            print("No analysis results. Run analyze_text() first.")
            return

        results = self.analysis_results
        print("\n" + "="*60)
        print("PDF ANALYSIS SUMMARY")
        print("="*60)
        print(f"File: {results['file_name']}")
        print(f"Pages: {results['total_pages']}")
        print(f"Characters: {results['total_characters']:,}")
        print(f"Total Words: {results['total_words']:,}")
        print(f"Unique Words: {results['unique_words']:,}")
        print(f"Average Word Length: {results['average_word_length']}")
        print(f"Estimated Sentences: {results['estimated_sentences']}")
        print(f"Lexical Diversity: {results['lexical_diversity']}")
        print("\nTop 10 Most Frequent Words:")
        print("-" * 40)
        for i, word_data in enumerate(results['top_20_words'][:10], 1):
            print(f"{i:2d}. {word_data['word']:20s} {word_data['count']:5d}")
        print("="*60 + "\n")


def main():
    """Main function demonstrating usage"""
    import sys

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python pdf_analyzer.py <pdf_file_path>")
        print("\nExample: python pdf_analyzer.py sample.pdf")
        print("\nThis will generate:")
        print("  - sample_analysis.json (full analysis)")
        print("  - sample_word_frequency.csv (word frequencies)")
        return

    pdf_file = sys.argv[1]

    # Create analyzer instance
    analyzer = PDFAnalyzer(pdf_file)

    # Extract text from PDF
    print("\n[1/4] Extracting text from PDF...")
    if not analyzer.extract_text():
        return

    # Analyze the extracted text
    print("\n[2/4] Analyzing text...")
    analyzer.analyze_text()

    # Print summary to console
    print("\n[3/4] Generating summary...")
    analyzer.print_summary()

    # Export results
    print("[4/4] Exporting results...")
    analyzer.export_to_json()
    analyzer.export_to_csv()

    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()
