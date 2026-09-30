"""
Plagiarism Detector - Compare multiple text documents for similarity
Uses difflib and advanced NLP techniques to detect plagiarism
"""

import difflib
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
import json


@dataclass
class SimilarityResult:
    """Store similarity comparison results between two documents"""
    doc1_name: str
    doc2_name: str
    similarity_score: float
    matching_blocks: List[Tuple[int, int, int]]
    matching_text: List[str]


class PlagiarismDetector:
    """Detect plagiarism between multiple text documents"""

    def __init__(self, min_match_length: int = 20):
        """
        Initialize plagiarism detector

        Args:
            min_match_length: Minimum character length for a match to be considered
        """
        self.min_match_length = min_match_length
        self.documents: Dict[str, str] = {}

    def add_document(self, name: str, content: str):
        """
        Add a document to the detector

        Args:
            name: Document identifier/name
            content: Document text content
        """
        self.documents[name] = self._preprocess_text(content)

    def load_document_from_file(self, filepath: str):
        """
        Load a document from a file

        Args:
            filepath: Path to the text file
        """
        path = Path(filepath)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.add_document(path.name, content)

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for comparison

        Args:
            text: Raw text content

        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for case-insensitive comparison

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        return text.lower()

    def compare_documents(self, doc1_name: str, doc2_name: str,
                         case_sensitive: bool = False) -> SimilarityResult:
        """
        Compare two documents for similarity

        Args:
            doc1_name: Name of first document
            doc2_name: Name of second document
            case_sensitive: Whether to perform case-sensitive comparison

        Returns:
            SimilarityResult object with comparison details
        """
        if doc1_name not in self.documents:
            raise ValueError(f"Document '{doc1_name}' not found")
        if doc2_name not in self.documents:
            raise ValueError(f"Document '{doc2_name}' not found")

        text1 = self.documents[doc1_name]
        text2 = self.documents[doc2_name]

        # Normalize for comparison if case-insensitive
        if not case_sensitive:
            compare_text1 = self._normalize_text(text1)
            compare_text2 = self._normalize_text(text2)
        else:
            compare_text1 = text1
            compare_text2 = text2

        # Use SequenceMatcher for comparison
        matcher = difflib.SequenceMatcher(None, compare_text1, compare_text2)

        # Get similarity ratio
        similarity_score = matcher.ratio()

        # Get matching blocks
        matching_blocks = matcher.get_matching_blocks()

        # Extract matching text segments (using original text for display)
        matching_text = []
        for block in matching_blocks:
            start, _, length = block
            if length >= self.min_match_length:
                match = text1[start:start + length]
                matching_text.append(match)

        return SimilarityResult(
            doc1_name=doc1_name,
            doc2_name=doc2_name,
            similarity_score=similarity_score,
            matching_blocks=matching_blocks,
            matching_text=matching_text
        )

    def compare_all_documents(self, case_sensitive: bool = False) -> List[SimilarityResult]:
        """
        Compare all documents against each other

        Args:
            case_sensitive: Whether to perform case-sensitive comparison

        Returns:
            List of SimilarityResult objects for all comparisons
        """
        results = []
        doc_names = list(self.documents.keys())

        # Compare each pair of documents
        for i in range(len(doc_names)):
            for j in range(i + 1, len(doc_names)):
                result = self.compare_documents(
                    doc_names[i],
                    doc_names[j],
                    case_sensitive
                )
                results.append(result)

        return results

    def generate_report(self, results: List[SimilarityResult],
                       output_format: str = 'text') -> str:
        """
        Generate a report from comparison results

        Args:
            results: List of SimilarityResult objects
            output_format: 'text', 'html', or 'json'

        Returns:
            Formatted report string
        """
        if output_format == 'text':
            return self._generate_text_report(results)
        elif output_format == 'html':
            return self._generate_html_report(results)
        elif output_format == 'json':
            return self._generate_json_report(results)
        else:
            raise ValueError(f"Unknown format: {output_format}")

    def _generate_text_report(self, results: List[SimilarityResult]) -> str:
        """Generate plain text report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("PLAGIARISM DETECTION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTotal Documents: {len(self.documents)}")
        report_lines.append(f"Total Comparisons: {len(results)}")
        report_lines.append("\n" + "=" * 80)

        # Sort results by similarity score (highest first)
        sorted_results = sorted(results, key=lambda x: x.similarity_score, reverse=True)

        for i, result in enumerate(sorted_results, 1):
            report_lines.append(f"\n{i}. Comparison: {result.doc1_name} vs {result.doc2_name}")
            report_lines.append("-" * 80)

            # Calculate percentage
            percentage = result.similarity_score * 100
            report_lines.append(f"Similarity Score: {result.similarity_score:.4f} ({percentage:.2f}%)")

            # Determine plagiarism level
            if percentage >= 80:
                level = "HIGH RISK - Likely Plagiarism"
            elif percentage >= 50:
                level = "MEDIUM RISK - Significant Similarity"
            elif percentage >= 25:
                level = "LOW RISK - Some Similarity"
            else:
                level = "MINIMAL - Little to No Similarity"

            report_lines.append(f"Risk Level: {level}")
            report_lines.append(f"\nMatching Segments: {len(result.matching_text)}")

            if result.matching_text:
                report_lines.append("\nMatching Text Samples:")
                for j, match in enumerate(result.matching_text[:5], 1):  # Show first 5
                    preview = match[:100] + "..." if len(match) > 100 else match
                    report_lines.append(f"  [{j}] {preview}")

                if len(result.matching_text) > 5:
                    report_lines.append(f"  ... and {len(result.matching_text) - 5} more matches")

            report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def _generate_html_report(self, results: List[SimilarityResult]) -> str:
        """Generate HTML report with highlighting"""
        html_parts = []
        html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Plagiarism Detection Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .comparison {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .score {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .high-risk { color: #e74c3c; }
        .medium-risk { color: #f39c12; }
        .low-risk { color: #f1c40f; }
        .minimal-risk { color: #2ecc71; }
        .match {
            background-color: #fff9c4;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #fbc02d;
            font-family: monospace;
        }
        .summary {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .summary-item {
            text-align: center;
        }
        .summary-number {
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Plagiarism Detection Report</h1>
        <div class="summary">
            <div class="summary-item">
                <div class="summary-number">""" + str(len(self.documents)) + """</div>
                <div>Documents</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">""" + str(len(results)) + """</div>
                <div>Comparisons</div>
            </div>
        </div>
    </div>
""")

        # Sort results by similarity score (highest first)
        sorted_results = sorted(results, key=lambda x: x.similarity_score, reverse=True)

        for i, result in enumerate(sorted_results, 1):
            percentage = result.similarity_score * 100

            # Determine risk level and class
            if percentage >= 80:
                level = "HIGH RISK - Likely Plagiarism"
                risk_class = "high-risk"
            elif percentage >= 50:
                level = "MEDIUM RISK - Significant Similarity"
                risk_class = "medium-risk"
            elif percentage >= 25:
                level = "LOW RISK - Some Similarity"
                risk_class = "low-risk"
            else:
                level = "MINIMAL - Little to No Similarity"
                risk_class = "minimal-risk"

            html_parts.append(f"""
    <div class="comparison">
        <h2>{i}. {result.doc1_name} vs {result.doc2_name}</h2>
        <div class="score {risk_class}">{percentage:.2f}%</div>
        <p><strong>Risk Level:</strong> {level}</p>
        <p><strong>Matching Segments:</strong> {len(result.matching_text)}</p>
""")

            if result.matching_text:
                html_parts.append("        <h3>Matching Text Samples:</h3>")
                for match in result.matching_text[:5]:
                    preview = match[:200] + "..." if len(match) > 200 else match
                    html_parts.append(f'        <div class="match">{self._escape_html(preview)}</div>')

                if len(result.matching_text) > 5:
                    html_parts.append(f"        <p><em>... and {len(result.matching_text) - 5} more matches</em></p>")

            html_parts.append("    </div>")

        html_parts.append("""
</body>
</html>
""")

        return "".join(html_parts)

    def _generate_json_report(self, results: List[SimilarityResult]) -> str:
        """Generate JSON report"""
        report_data = {
            "total_documents": len(self.documents),
            "total_comparisons": len(results),
            "documents": list(self.documents.keys()),
            "comparisons": []
        }

        for result in results:
            percentage = result.similarity_score * 100

            if percentage >= 80:
                level = "HIGH_RISK"
            elif percentage >= 50:
                level = "MEDIUM_RISK"
            elif percentage >= 25:
                level = "LOW_RISK"
            else:
                level = "MINIMAL"

            comparison = {
                "document1": result.doc1_name,
                "document2": result.doc2_name,
                "similarity_score": result.similarity_score,
                "similarity_percentage": round(percentage, 2),
                "risk_level": level,
                "matching_segments_count": len(result.matching_text),
                "matching_text_samples": result.matching_text[:5]
            }
            report_data["comparisons"].append(comparison)

        return json.dumps(report_data, indent=2)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def main():
    """Example usage of the plagiarism detector"""
    print("Plagiarism Detector - Example Usage\n")

    # Create detector instance
    detector = PlagiarismDetector(min_match_length=20)

    # Sample documents for demonstration
    doc1 = """
    Machine learning is a subset of artificial intelligence that focuses on the development
    of algorithms and statistical models that enable computer systems to improve their
    performance on a specific task through experience. Machine learning algorithms build
    a mathematical model based on sample data, known as training data, in order to make
    predictions or decisions without being explicitly programmed to perform the task.
    """

    doc2 = """
    Machine learning is a subset of artificial intelligence that focuses on the development
    of algorithms and statistical models. These algorithms enable computer systems to improve
    their performance on specific tasks through experience and learning from data.
    """

    doc3 = """
    Deep learning is a subset of machine learning that uses neural networks with multiple
    layers. These deep neural networks attempt to simulate the behavior of the human brain,
    allowing them to learn from large amounts of data. While a neural network with a single
    layer can still make approximate predictions, additional hidden layers can help optimize
    the accuracy of the results.
    """

    doc4 = """
    The weather today is beautiful with clear blue skies. It's a perfect day for outdoor
    activities like hiking, biking, or simply enjoying a picnic in the park. The temperature
    is mild and comfortable, making it ideal for spending time outside with family and friends.
    """

    # Add documents
    print("Adding documents...")
    detector.add_document("Document_1.txt", doc1)
    detector.add_document("Document_2.txt", doc2)
    detector.add_document("Document_3.txt", doc3)
    detector.add_document("Document_4.txt", doc4)

    # Compare all documents
    print("Analyzing documents for plagiarism...\n")
    results = detector.compare_all_documents(case_sensitive=False)

    # Generate and display text report
    text_report = detector.generate_report(results, output_format='text')
    print(text_report)

    # Save HTML report
    html_report = detector.generate_report(results, output_format='html')
    with open('plagiarism_report.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("\n✓ HTML report saved to: plagiarism_report.html")

    # Save JSON report
    json_report = detector.generate_report(results, output_format='json')
    with open('plagiarism_report.json', 'w', encoding='utf-8') as f:
        f.write(json_report)
    print("✓ JSON report saved to: plagiarism_report.json")


if __name__ == "__main__":
    main()
