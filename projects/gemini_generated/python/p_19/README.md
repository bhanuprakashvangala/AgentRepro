# Markdown to HTML Converter

This project is a Python script that converts a Markdown file into a fully-styled, self-contained HTML file. It includes support for syntax highlighting in code blocks and automatically generates a table of contents.

## Features

- **Table of Contents**: Automatically generates a TOC from the document's headers by including `[TOC]` in the Markdown file.
- **Syntax Highlighting**: Uses the `Pygments` library to apply color and styling to fenced code blocks (e.g., ` ```python `).
- **Self-Contained HTML**: All necessary CSS for both document styling and syntax highlighting is embedded directly into the output HTML file, making it fully portable.
- **Reproducible Demo**: The script generates its own `sample.md` file on first run, allowing for immediate demonstration of all features.

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

3.  **Run the script:**
    ```bash
    python md_converter.py
    ```

## Output

When you run the script, it will:

1.  Create a `sample.md` file with example content.
2.  Convert this file into `output.html`.

Open `output.html` in any web browser to see the final, styled document. You will see a table of contents at the top, followed by the formatted content, including a code block with syntax highlighting.
