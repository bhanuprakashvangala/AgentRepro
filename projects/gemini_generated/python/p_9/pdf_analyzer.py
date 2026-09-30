import pdfplumber
import json
import re
from collections import Counter
import os

# reportlab is used to generate a sample PDF for reproducibility
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf(filename="sample.pdf"):
    """Creates a simple, multi-page PDF for demonstration purposes."""
    if os.path.exists(filename):
        print(f"Sample PDF '{filename}' already exists.")
        return

    print(f"Creating sample PDF: {filename}")
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Page 1
    c.drawString(72, height - 72, "This is the first page of the document.")
    c.drawString(72, height - 90, "This document is a simple test. The purpose of this test is to demonstrate PDF text extraction.")
    c.showPage()

    # Page 2
    c.drawString(72, height - 72, "This is the second page, which has different text.")
    c.drawString(72, height - 90, "Text extraction can be tricky. This is a simple document.")
    c.showPage()

    c.save()
    print("Sample PDF created successfully.")

def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Extracting text from {len(pdf.pages)} pages...")
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    print("Text extraction complete.")
    return full_text

def analyze_text(text):
    """Performs word count and frequency analysis on the extracted text."""
    print("Analyzing text...")
    # Use regex to find all words, converting to lowercase
    words = re.findall(r'\b\w+\b', text.lower())
    
    total_word_count = len(words)
    word_frequency = Counter(words)
    
    analysis = {
        "total_word_count": total_word_count,
        "unique_word_count": len(word_frequency),
        "word_frequency": dict(word_frequency.most_common(20)) # Get top 20 most common
    }
    print("Analysis complete.")
    return analysis

def export_to_json(analysis_data, output_filename="analysis_results.json"):
    """Exports the analysis results to a JSON file."""
    print(f"Exporting results to {output_filename}...")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=4)
    print("Export complete.")

if __name__ == "__main__":
    PDF_FILENAME = "sample.pdf"
    JSON_OUTPUT_FILENAME = "analysis_results.json"
    
    print("--- Starting PDF Text Extraction and Analysis Tool ---")
    # 1. Create a sample PDF to work with
    create_sample_pdf(PDF_FILENAME)
    
    # 2. Extract text from the PDF
    extracted_text = extract_text_from_pdf(PDF_FILENAME)
    
    # 3. Analyze the extracted text
    text_analysis = analyze_text(extracted_text)
    
    # 4. Export the results to JSON
    export_to_json(text_analysis, JSON_OUTPUT_FILENAME)
    
    print("\n--- Process Finished Successfully ---")
    print(f"Check the generated '{JSON_OUTPUT_FILENAME}' for the analysis.")
