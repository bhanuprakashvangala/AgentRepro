# Extractive Text Summarizer

This is a command-line tool that generates a concise, extractive summary of one or more text documents. It uses the `sumy` library with the LSA (Latent Semantic Analysis) summarization algorithm.

## Features

- **Extractive Summarization**: The tool identifies and combines the most important sentences from the original text to create a summary.
- **Configurable Length**: You can specify the desired length of the summary in sentences.
- **Batch Processing**: Supports summarizing multiple documents in a single command.
- **Reproducible Demo**: Includes a `--demo` mode that automatically generates sample articles and summarizes them, providing a quick and easy end-to-end test.
- **Automatic Setup**: On the first run, the script automatically downloads the necessary `punkt` tokenizer data from `nltk`.

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

3.  **(Recommended) Run the Demo:**
    This is the best way to see the tool in action. It will create a `demo_texts/` directory with two sample articles and then generate summaries for them.
    ```bash
    python summarizer.py --demo
    ```

4.  **Summarize Your Own File(s):**
    Provide the path to one or more text files. You can use the `--length` (or `-l`) flag to control the number of sentences in the summary.

    **Summarize a single file:**
    ```bash
    python summarizer.py my_article.txt
    ```

    **Summarize multiple files with a 5-sentence summary:**
    ```bash
    python summarizer.py report.txt notes.txt --length 5
    ```

## Output

For each file processed, the script will print the generated summary to the console and save it to a new file with a `.summary.txt` extension in the same directory.

**Example Output for Demo:**
```
--- Summarizing: demo_texts\article1.txt ---

Summary:
It is a gas giant with a mass more than two and a half times that of all the other planets in the Solar System combined, but slightly less than one-thousandth the mass of the Sun. Jupiter is the third brightest natural object in the Earth's night sky after the Moon and Venus. When viewed from Earth, Jupiter can be bright enough for its reflected light to cast visible shadows.

 -> Saved summary to: demo_texts\article1.summary.txt
...
```
