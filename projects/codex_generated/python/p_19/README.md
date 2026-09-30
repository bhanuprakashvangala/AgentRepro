# Markdown to HTML Converter

Converts Markdown files into styled HTML pages with syntax-highlighted code blocks and an optional table of contents.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python md_to_html.py --input README.md --output README.html --title "Project Docs"
```

Options:
- `--no-toc`: Disable table of contents generation.
- `--extra-css path.css`: Embed additional CSS rules.
- `--encoding`: Specify file encoding (default `utf-8`).

The generated HTML includes built-in styling and Pygments-based highlighting for fenced code blocks with language specifiers (```python, ```js, etc.).
