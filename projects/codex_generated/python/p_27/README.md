# Face Detection with OpenCV

Detects faces in batches of images using the Haar cascade classifier bundled with OpenCV and writes annotated copies with bounding boxes.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python face_detector.py --inputs photos/ --output-dir annotated/
```

Options:
- `--inputs`: One or more image files or directories (searched recursively).
- `--output-dir`: Destination directory for annotated images (required).
- `--cascade`: Path to a Haar cascade XML (defaults to OpenCV's frontal-face model).
- `--scale-factor`: Image pyramid scale for detection (default `1.1`).
- `--min-neighbors`: Detection confidence threshold (default `5`).
- `--min-size`: Minimum face size in pixels (default `30`).

Example detecting with a custom cascade and stricter threshold:
```bash
python face_detector.py \
  --inputs portraits/*.jpg \
  --output-dir tagged \
  --scale-factor 1.2 \
  --min-neighbors 6 \
  --min-size 40
```

Each processed image is saved with rectangles around detected faces, and a summary is printed to the console.
