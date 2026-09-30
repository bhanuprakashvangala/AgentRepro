#!/usr/bin/env python3
"""Convert Markdown to styled HTML with syntax highlighting and TOC."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from markdown import Markdown
from pygments.formatters import HtmlFormatter

DEFAULT_EXTENSIONS = [
    "toc",
    "fenced_code",
    "codehilite",
    "tables",
    "sane_lists",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Markdown to HTML converter with highlighting")
    parser.add_argument("--input", required=True, help="Input Markdown file")
    parser.add_argument("--output", required=True, help="Output HTML file")
    parser.add_argument(
        "--title",
        default="Document",
        help="Title for the HTML page",
    )
    parser.add_argument(
        "--no-toc",
        action="store_true",
        help="Disable automatic table of contents",
    )
    parser.add_argument(
        "--extra-css",
        help="Path to an additional CSS file to embed",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding for input/output (default: utf-8)",
    )
    return parser.parse_args()


def build_markdown(no_toc: bool) -> Markdown:
    extensions = [ext for ext in DEFAULT_EXTENSIONS if not (no_toc and ext == "toc")]
    extension_configs = {
        "toc": {
            "permalink": True,
            "title": "Table of Contents",
        },
        "codehilite": {
            "guess_lang": False,
            "pygments_style": "default",
            "noclasses": False,
        },
    }
    return Markdown(extensions=extensions, extension_configs=extension_configs)


def generate_css(extra_css_path: Path | None) -> str:
    formatter = HtmlFormatter(style="default")
    css_parts = [formatter.get_style_defs(".codehilite")]
    base_css = """
body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; margin: 2rem auto; max-width: 900px; padding: 0 1rem; background: #f8f9fa; color: #212529; }
h1, h2, h3, h4, h5, h6 { color: #102a43; }
a { color: #1d72b8; }
pre { background: #272822; color: #f8f8f2; padding: 1rem; border-radius: 6px; overflow: auto; }
code { font-family: 'Fira Code', 'Source Code Pro', monospace; }
nav.toc { background: #ffffff; border: 1px solid #d0d7de; border-radius: 6px; padding: 1rem; margin-bottom: 2rem; }
nav.toc ul { list-style: none; padding-left: 0; }
nav.toc li { margin: 0.25rem 0; }
    """
    css_parts.append(base_css)
    if extra_css_path:
        css_parts.append(extra_css_path.read_text(encoding="utf-8"))
    return "\n".join(css_parts)


def convert_markdown(input_path: Path, no_toc: bool, encoding: str) -> tuple[str, str]:
    md = build_markdown(no_toc)
    text = input_path.read_text(encoding=encoding)
    html_body = md.convert(text)
    toc_html = md.toc if "toc" in md.registeredExtensions and not no_toc else ""
    return html_body, toc_html


def build_html(title: str, body: str, toc: str, css: str) -> str:
    toc_section = f"<nav class='toc'>{toc}</nav>" if toc else ""
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
{css}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
  </header>
  {toc_section}
  <main>
    {body}
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    extra_css_path = Path(args.extra_css) if args.extra_css else None
    if extra_css_path and not extra_css_path.exists():
        print(f"Error: extra CSS file not found: {extra_css_path}", file=sys.stderr)
        sys.exit(1)

    body_html, toc_html = convert_markdown(input_path, args.no_toc, args.encoding)
    css = generate_css(extra_css_path)
    final_html = build_html(args.title, body_html, toc_html, css)

    output_path = Path(args.output)
    output_path.write_text(final_html, encoding=args.encoding)
    print(f"Converted {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
