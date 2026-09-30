#!/usr/bin/env python3
"""
Markdown to HTML Converter with Syntax Highlighting
Converts markdown documents to styled HTML with code syntax highlighting
"""

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeBlockExtension
from markdown.extensions.toc import TocExtension
from pygments.formatters import HtmlFormatter
import sys
import argparse
from pathlib import Path


def get_css_styles():
    """Generate CSS styles including Pygments syntax highlighting"""
    # Get Pygments CSS for syntax highlighting
    formatter = HtmlFormatter(style='monokai')
    pygments_css = formatter.get_style_defs('.codehilite')

    # Additional CSS for styling
    custom_css = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }

        .container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }

        h1 {
            font-size: 2em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }

        h2 {
            font-size: 1.5em;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }

        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: 0.875em; }
        h6 { font-size: 0.85em; color: #6a737d; }

        code {
            background-color: rgba(27,31,35,0.05);
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 85%;
            padding: 0.2em 0.4em;
        }

        pre {
            background-color: #272822;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
        }

        pre code {
            background-color: transparent;
            padding: 0;
            color: #f8f8f2;
        }

        .codehilite {
            background-color: #272822;
            border-radius: 6px;
            padding: 16px;
            overflow: auto;
        }

        blockquote {
            border-left: 4px solid #dfe2e5;
            color: #6a737d;
            padding-left: 16px;
            margin-left: 0;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }

        table th, table td {
            border: 1px solid #dfe2e5;
            padding: 8px 13px;
        }

        table th {
            background-color: #f6f8fa;
            font-weight: 600;
        }

        table tr:nth-child(even) {
            background-color: #f6f8fa;
        }

        a {
            color: #0366d6;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        img {
            max-width: 100%;
            height: auto;
        }

        hr {
            border: none;
            border-top: 1px solid #eaecef;
            margin: 24px 0;
        }

        ul, ol {
            padding-left: 2em;
        }

        li {
            margin: 0.25em 0;
        }

        .toc {
            background-color: #f6f8fa;
            border: 1px solid #dfe2e5;
            border-radius: 6px;
            padding: 16px 24px;
            margin: 24px 0;
        }

        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }

        .toc ul ul {
            padding-left: 20px;
        }

        .toc a {
            color: #0366d6;
        }

        .toc-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 12px;
        }
    """

    return f"<style>\n{custom_css}\n{pygments_css}\n</style>"


def convert_markdown_to_html(markdown_text, include_toc=True):
    """
    Convert markdown text to HTML with syntax highlighting

    Args:
        markdown_text: The markdown content as a string
        include_toc: Whether to generate a table of contents

    Returns:
        HTML string with styling and syntax highlighting
    """
    # Configure markdown extensions
    extensions = [
        FencedCodeBlockExtension(),
        CodeHiliteExtension(
            linenums=False,
            guess_lang=True,
            css_class='codehilite'
        ),
        'tables',
        'nl2br',
        'sane_lists',
    ]

    if include_toc:
        extensions.append(TocExtension(
            title='Table of Contents',
            toc_depth='2-3',
            marker='[TOC]'
        ))

    # Create markdown instance
    md = markdown.Markdown(extensions=extensions)

    # Convert markdown to HTML
    html_content = md.convert(markdown_text)

    # Build complete HTML document
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Document</title>
    {get_css_styles()}
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>"""

    return html_template


def convert_file(input_file, output_file=None, include_toc=True):
    """
    Convert a markdown file to HTML

    Args:
        input_file: Path to input markdown file
        output_file: Path to output HTML file (optional)
        include_toc: Whether to generate table of contents
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Read markdown content
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # Convert to HTML
    html_output = convert_markdown_to_html(markdown_text, include_toc)

    # Determine output file
    if output_file is None:
        output_file = input_path.with_suffix('.html')

    # Write HTML output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"Successfully converted '{input_file}' to '{output_file}'")
    return output_file


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Convert Markdown to HTML with syntax highlighting'
    )
    parser.add_argument(
        'input',
        help='Input markdown file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output HTML file (default: input file with .html extension)'
    )
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='Disable table of contents generation'
    )

    args = parser.parse_args()

    try:
        convert_file(
            args.input,
            args.output,
            include_toc=not args.no_toc
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
