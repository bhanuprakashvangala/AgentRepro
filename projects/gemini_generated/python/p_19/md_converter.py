import markdown
import os
from pygments.formatters import HtmlFormatter

INPUT_FILE = "sample.md"
OUTPUT_FILE = "output.html"

def generate_sample_markdown(filename=INPUT_FILE):
    """Generates a sample Markdown file for demonstration."""
    if os.path.exists(filename):
        print(f"Sample file '{filename}' already exists.")
        return

    print(f"Generating sample file: {filename}")
    md_content = """[TOC]

# Markdown to HTML Converter Demo

This document demonstrates the features of the converter, including a Table of Contents, styled text, and syntax highlighting.

## Section 1: Python Code Example

Below is a fenced code block identified as Python. The `codehilite` extension uses Pygments to apply syntax highlighting.

```python
def greet(name):
    """A simple function to greet someone."""
    message = f"Hello, {name}!"
    print(message)

# Call the function
greet("World")
```

## Section 2: Other Elements

This converter also supports standard Markdown elements.

- Unordered list item 1
- Unordered list item 2

1. Ordered list item 1
2. Ordered list item 2

> This is a blockquote.
"""
    with open(filename, 'w') as f:
        f.write(md_content)

def convert_markdown_to_html(input_file, output_file):
    """Reads a Markdown file, converts it to HTML with styling, and saves it."""
    print(f"Converting {input_file} to {output_file}...")
    
    try:
        with open(input_file, 'r') as f:
            md_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return

    # --- CSS Generation ---
    # Get CSS for Pygments syntax highlighting (using the 'default' theme)
    formatter = HtmlFormatter(style='default', full=True, cssclass='codehilite')
    pygments_css = formatter.get_style_defs()

    # Basic CSS for the document body and Table of Contents
    body_css = """
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        .toc { background-color: #f8f8f8; border: 1px solid #e0e0e0; padding: 10px 20px; border-radius: 5px; }
        .toc ul { list-style-type: none; padding-left: 0; }
        .codehilite { background: #f6f8fa; padding: 1em; border-radius: 5px; }
    """
    full_css = f"<style>\n{body_css}\n{pygments_css}\n</style>"

    # --- Markdown Conversion ---
    # Configure extensions
    extensions = [
        'toc',          # Table of Contents
        'fenced_code',  # Support for ```code``` blocks
        'codehilite'    # Syntax highlighting
    ]
    extension_configs = {
        'codehilite': {
            'css_class': 'codehilite', # Class name for the code block div
            'linenums': False         # Set to True to add line numbers
        }
    }

    html_body = markdown.markdown(
        md_text, 
        extensions=extensions, 
        extension_configs=extension_configs
    )

    # --- Assemble Final HTML Document ---
    final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(input_file)}</title>
    {full_css}
</head>
<body>
    {html_body}
</body>
</html>"""

    with open(output_file, 'w') as f:
        f.write(final_html)
    
    print(f"Successfully converted and saved to {output_file}")

if __name__ == "__main__":
    print("--- Markdown to HTML Converter ---")
    generate_sample_markdown()
    convert_markdown_to_html(INPUT_FILE, OUTPUT_FILE)
    print(f"\nProcess complete. Open '{OUTPUT_FILE}' in a browser to see the result.")
