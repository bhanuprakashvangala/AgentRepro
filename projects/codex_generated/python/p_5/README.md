# Pretrained Image Classifier

This script classifies images in a folder using the pretrained ResNet-50 model from torchvision. It generates predictions with confidence scores and stores them in a CSV file.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Place your images in a directory (e.g., `images/`) and run:

```bash
python classify_images.py --input-dir images --output predictions.csv --top-k 3
```

Options:
- `--input-dir`: Folder containing images (required).
- `--output`: CSV file to write results (`predictions.csv` by default).
- `--top-k`: Number of top predictions to return per image (default `1`).
- `--recursive`: Search for images in subdirectories.
- `--device`: Force `cpu` or `cuda` (defaults to auto-detection).

The output CSV contains columns `image`, `label`, and `confidence`. Confidence values are softmax probabilities (0-1). The script skips unreadable files and logs errors to stderr.
