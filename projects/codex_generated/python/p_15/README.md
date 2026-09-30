# QR Code Tool

CLI utility that generates QR codes from custom data and reads QR codes from existing images. Supports bulk operations via data files and recursive directory scanning.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate QR codes

### From command-line data
```bash
python qr_tool.py generate --data "Hello world" "https://example.com" --output-dir qr_codes
```

### From a CSV/text file (one value per line/first column)
```bash
python qr_tool.py generate --data-file urls.csv --prefix link_ --image-format jpg
```

## Read QR codes

```bash
python qr_tool.py read --input qr_codes --recursive --output decoded.csv
```

This scans `qr_codes/` for PNG/JPG/BMP images, extracts QR payloads, prints them, and saves `decoded.csv` with `file,data` columns. Customize recognized extensions with `--extensions`.

> OpenCV is used for decoding; the script warns when an image cannot be processed.
