# HTML to PDF Service

Generate PDFs from HTML/Pug templates using Puppeteer. Includes CLI and Express endpoint, plus scheduling support for custom page size, margins, header/footer content.

## Setup
```bash
npm install
```
Puppeteer downloads Chromium automatically. Behind proxies set appropriate env vars.

## CLI Usage
```bash
node generate.js --template invoice --data data/sample-invoice.json --output output.pdf --format A4 --margin '{"top":"20mm","bottom":"25mm","left":"15mm","right":"15mm"}'
```
- `--template`: template name (looks for `.pug` or `.html` in `/templates`).
- `--data`: JSON file with template context.
- `--output`: Output PDF path.
- optional: `--format`, `--width`, `--height`, `--margin` (JSON), `--headerTemplate`, `--footerTemplate` (HTML file paths).

## HTTP Service
```bash
npm start
```
POST `/generate` with JSON:
```json
{
  "templateName": "invoice",
  "data": { "company": "Acme" },
  "page": {
    "format": "A4",
    "margin": { "top": "20mm", "bottom": "25mm" }
  },
  "headerTemplate": "<div style='font-size:10px;width:100%;text-align:center;'>Acme Corp</div>",
  "footerTemplate": "<div style='font-size:10px;width:100%;text-align:center;'>Page <span class='pageNumber'></span> of <span class='totalPages'></span></div>"
}
```
Returns generated PDF.

## Templates
- `templates/invoice.pug` – sample invoice.
- `data/sample-invoice.json` – example data.

Modify templates or add new ones as needed. Margins accept CSS units (mm, in, px). Header/footer HTML must fit Puppeteer expectations.
