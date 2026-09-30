import os
import argparse
import nltk
from difflib import SequenceMatcher

# --- Configuration ---
SIMILARITY_THRESHOLD = 0.85 # Consider sentences with >= 85% similarity as a match
DEMO_DIR = "demo_texts"

def download_nltk_data():
    """Downloads the 'punkt' tokenizer if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except nltk.downloader.DownloadError:
        print("[INFO] Downloading 'punkt' tokenizer for NLTK...")
        nltk.download('punkt')
        print("[INFO] Download complete.")

def setup_demo_files():
    """Creates a set of sample text files for a reproducible demo."""
    if not os.path.exists(DEMO_DIR): os.makedirs(DEMO_DIR)

    demo_content = {
        "source.txt": """
            The solar system is a gravitationally bound system of the Sun and the objects that orbit it. 
            It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud. 
            The vast majority of the system's mass is in the Sun, with most of the remaining mass contained in the planet Jupiter. 
            The four inner terrestrial planets are Mercury, Venus, Earth and Mars. 
            These planets are small and composed of rock and metal.
            ",
        "original1.txt": """
            Our solar system consists of the Sun and everything that orbits it. 
            It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud. 
            The four inner terrestrial planets are Mercury, Venus, Earth and Mars. 
            They are primarily made of rock and metal.
            ",
        "original2.txt": """
            The planet Jupiter contains most of the remaining mass in the solar system, second only to the Sun. 
            It is a gas giant, unlike the inner planets.
            ",
        "unrelated.txt": """
            The ocean is a huge body of saltwater that covers about 71 percent of Earth's surface. 
            The planet has one global ocean, though oceanographers and the countries of the world have traditionally divided it into four distinct regions: the Pacific, Atlantic, Indian, and Arctic oceans.
            "
    }
    for filename, content in demo_content.items():
        path = os.path.join(DEMO_DIR, filename)
        if not os.path.exists(path):
            print(f"Generating demo file: {path}")
            with open(path, 'w') as f:
                f.write(content)

def compare_documents(source_path, comparison_path, threshold):
    """Compares two documents sentence by sentence and finds matches."""
    try:
        with open(source_path, 'r') as f: source_text = f.read()
        with open(comparison_path, 'r') as f: comparison_text = f.read()
    except FileNotFoundError as e:
        print(f"[ERROR] Could not open file: {e}. Skipping comparison.")
        return [], 0

    source_sentences = nltk.sent_tokenize(source_text)
    comparison_sentences = nltk.sent_tokenize(comparison_text)
    
    if not source_sentences or not comparison_sentences:
        return [], 0

    matching_sections = []
    for s1 in source_sentences:
        best_match_ratio = 0
        best_match_sentence = ""
        for s2 in comparison_sentences:
            ratio = SequenceMatcher(None, s1, s2).ratio()
            if ratio > best_match_ratio:
                best_match_ratio = ratio
                best_match_sentence = s2
        
        if best_match_ratio >= threshold:
            matching_sections.append({
                "source_sentence": s1.strip(),
                "match_sentence": best_match_sentence.strip(),
                "similarity": best_match_ratio
            })
            
    return matching_sections, len(source_sentences)

def generate_report(source_path, comparison_path, matches, total_source_sentences):
    """Generates a text report of the plagiarism analysis."""
    output_filename = f"report_{{os.path.basename(source_path)}}_vs_{{os.path.basename(comparison_path)}}.txt"
    print(f" -> Generating report: {output_filename}")

    plagiarism_percentage = (len(matches) / total_source_sentences) * 100 if total_source_sentences > 0 else 0

    with open(output_filename, 'w') as f:
        f.write("---" + " Plagiarism Analysis Report ---" + "\n\n")
        f.write(f"Source Document:      {source_path}\n")
        f.write(f"Comparison Document:  {comparison_path}\n")
        f.write(f"Timestamp:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n--- Summary ---" + "\n")
        f.write(f"Overall Similarity Score: {plagiarism_percentage:.2f}%\n")
        f.write(f"({len(matches)} out of {total_source_sentences} sentences in the source document were found to be similar.)\n")
        f.write("\n--- Highlighted Matching Sections ---" + "\n")

        if not matches:
            f.write("No significant similarities found.\n")
        else:
            for i, match in enumerate(matches):
                f.write(f"\nMatch {i+1} ({match['similarity']:.2%}% similarity):\n")
                f.write(f"  - Source:      \"{match['source_sentence']}\"\n")
                f.write(f"  - Found Match: \"{match['match_sentence']}\"\n")
    print("    Report complete.")

if __name__ == "__main__":
    download_nltk_data()
    parser = argparse.ArgumentParser(description="Detect plagiarism between text documents.")
    parser.add_argument("source_file", nargs='?', help="The source document to check.")
    parser.add_argument("comparison_files", nargs='*', help="One or more documents to compare against.")
    parser.add_argument("-t", "--threshold", type=float, default=SIMILARITY_THRESHOLD, help=f"Similarity threshold (0.0-1.0) to consider a sentence a match (default: {SIMILARITY_THRESHOLD}).")
    parser.add_argument("--demo", action="store_true", help="Run a demo with sample documents.")
    args = parser.parse_args()

    if args.demo:
        setup_demo_files()
        source = os.path.join(DEMO_DIR, "source.txt")
        comparisons = [os.path.join(DEMO_DIR, f) for f in ["original1.txt", "original2.txt", "unrelated.txt"]]
        print("Running demo...")
    elif args.source_file and args.comparison_files:
        source = args.source_file
        comparisons = args.comparison_files
    else:
        print("Please provide a source file and at least one comparison file, or use --demo.")
        parser.print_help()
        exit()

    for comp_file in comparisons:
        print(f"\nComparing '{source}' against '{comp_file}'...")
        found_matches, total_sentences = compare_documents(source, comp_file, args.threshold)
        if total_sentences > 0:
            generate_report(source, comp_file, found_matches, total_sentences)
    
    print("\n--- Process Complete ---")
