import os
import argparse
import nltk

# Sumy imports
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# --- Configuration ---
LANGUAGE = "english"
DEFAULT_SENTENCE_COUNT = 3

def download_nltk_data():
    """Downloads the 'punkt' tokenizer if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
    except nltk.downloader.DownloadError:
        print("[INFO] Downloading 'punkt' tokenizer for NLTK...")
        nltk.download('punkt')
        print("[INFO] Download complete.")

def setup_demo_files():
    """Creates sample text files for the demo."""
    demo_content = {
        "article1.txt": """
            Jupiter is the fifth planet from the Sun and the largest in the Solar System. 
            It is a gas giant with a mass more than two and a half times that of all the other planets in the Solar System combined, but slightly less than one-thousandth the mass of the Sun. 
            Jupiter is the third brightest natural object in the Earth's night sky after the Moon and Venus. 
            People have been observing it since prehistoric times; it was named after the Roman god Jupiter, the king of the gods. 
            When viewed from Earth, Jupiter can be bright enough for its reflected light to cast visible shadows.
            The planet is primarily composed of hydrogen, but helium constitutes one-quarter of its mass and one-tenth of its volume.
            ",
        "article2.txt": """
            The Red Planet, Mars, has been a subject of fascination for centuries. 
            Its distinct reddish hue is due to iron oxide prevalent on its surface. 
            Mars is a terrestrial planet with a thin atmosphere, having surface features reminiscent both of the impact craters of the Moon and the volcanoes, valleys, deserts, and polar ice caps of Earth. 
            The rotational period and seasonal cycles of Mars are likewise similar to those of Earth, as is the tilt that produces the seasons. 
            Mars is the site of Olympus Mons, the largest volcano and second-highest known mountain in the Solar System.
            "
    }
    if not os.path.exists("demo_texts"): os.makedirs("demo_texts")
    
    for filename, content in demo_content.items():
        path = os.path.join("demo_texts", filename)
        if not os.path.exists(path):
            print(f"Generating demo file: {path}")
            with open(path, 'w') as f:
                f.write(content)
    return [os.path.join("demo_texts", f) for f in demo_content.keys()]

def summarize_document(file_path, sentence_count):
    """Summarizes a single document and saves the summary to a file."""
    print(f"\n--- Summarizing: {file_path} ---")
    try:
        # Initialize the parser and summarizer
        parser = PlaintextParser.from_file(file_path, Tokenizer(LANGUAGE))
        summarizer = LsaSummarizer()

        # Generate the summary
        summary_sentences = summarizer(parser.document, sentence_count)
        
        summary = " ".join([str(sentence) for sentence in summary_sentences])

        # Print and save the summary
        print("\nSummary:")
        print(summary)

        output_filename = os.path.splitext(file_path)[0] + ".summary.txt"
        with open(output_filename, 'w') as f:
            f.write(summary)
        print(f"\n -> Saved summary to: {output_filename}")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure NLTK data is ready
    download_nltk_data()

    parser = argparse.ArgumentParser(description="Summarize text documents using extractive summarization.")
    parser.add_argument("files", nargs='*', help="Path(s) to text files to summarize.")
    parser.add_argument("-l", "--length", type=int, default=DEFAULT_SENTENCE_COUNT, help=f"Number of sentences in the summary (default: {DEFAULT_SENTENCE_COUNT}).")
    parser.add_argument("--demo", action="store_true", help="Run a demo with sample articles.")
    args = parser.parse_args()

    if args.demo:
        files_to_process = setup_demo_files()
    elif args.files:
        files_to_process = args.files
    else:
        parser.print_help()
        exit()

    for file_path in files_to_process:
        summarize_document(file_path, args.length)
    
    print("\n--- Process Complete ---")
