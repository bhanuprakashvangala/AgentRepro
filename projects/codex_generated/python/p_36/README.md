# Image Resize & Optimization Tool

Batch resizes and optimizes images using Pillow. Maintains aspect ratio by default, configurable target dimensions, quality, and format conversion.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python image_optimizer.py \
  --input photos/ logo.png \
  --output-dir optimized \
  --max-dimension 1200 \
  --quality 90
```

Options:
- `--width` / `--height`: Target dimension(s). When both provided with aspect ratio preserved, fits within the box.
- `--max-dimension`: Scale longest side to this size.
- `--no-keep-aspect`: Force exact width/height (may distort).
- `--format`: Convert to `jpeg`, `png`, `webp`, or `keep` original.
- `--quality`: JPEG/WebP quality (1-100, default 85).
- `--overwrite`: Replace existing files in output directory.

Each processed image is saved to the output directory with resized dimensions and optimized file size.
