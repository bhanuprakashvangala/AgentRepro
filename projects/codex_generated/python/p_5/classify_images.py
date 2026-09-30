#!/usr/bin/env python3
"""Classify images in a folder using a pretrained ResNet-50 model."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import ResNet50_Weights, resnet50

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify images in a directory using a pretrained ResNet-50 model."
    )
    parser.add_argument("--input-dir", required=True, help="Directory containing images to classify.")
    parser.add_argument(
        "--output",
        default="predictions.csv",
        help="CSV file to write predictions (image path, label, confidence).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help="Number of top predictions to save per image (default: 1).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for images recursively in subdirectories.",
    )
    parser.add_argument(
        "--device",
        default=None,
        choices=["cpu", "cuda", None],
        help="Device to run inference on (default: auto).",
    )
    return parser.parse_args()


def collect_image_paths(root: Path, recursive: bool) -> List[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Input directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {root}")

    if recursive:
        paths = [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS]
    else:
        paths = [p for p in root.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not paths:
        raise ValueError("No supported image files found in the provided directory.")

    return sorted(paths)


def load_model(device: torch.device) -> Tuple[torch.nn.Module, List[str], transforms.Compose]:
    weights = ResNet50_Weights.DEFAULT
    model = resnet50(weights=weights)
    model.eval()
    model.to(device)
    preprocess = weights.transforms()
    categories = weights.meta.get("categories", [])
    if not categories:
        raise RuntimeError("Unable to load category labels from pretrained weights metadata.")
    return model, categories, preprocess


def run_inference(
    model: torch.nn.Module,
    preprocess: transforms.Compose,
    categories: List[str],
    image_paths: Iterable[Path],
    device: torch.device,
    top_k: int,
) -> List[Tuple[str, str, float]]:
    results: List[Tuple[str, str, float]] = []
    softmax = torch.nn.Softmax(dim=1)

    for image_path in image_paths:
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Skipping {image_path}: failed to open image ({exc})", file=sys.stderr)
            continue

        input_tensor = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            logits = model(input_tensor)
            probabilities = softmax(logits)

        values, indices = probabilities.topk(top_k)
        for confidence, idx in zip(values.squeeze(0), indices.squeeze(0)):
            label = categories[idx.item()]
            results.append((str(image_path), label, float(confidence.item())))

    return results


def write_predictions(results: List[Tuple[str, str, float]], output_path: Path, top_k: int) -> None:
    fieldnames = ["image", "label", "confidence"]
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for image_path, label, confidence in results:
            writer.writerow(
                {
                    "image": image_path,
                    "label": label,
                    "confidence": f"{confidence:.4f}",
                }
            )

    print(f"Saved {len(results)} predictions to {output_path} (top_k={top_k}).")


def main() -> None:
    args = parse_args()

    input_dir = Path(args.input_dir)
    top_k = max(1, args.top_k)

    try:
        image_paths = collect_image_paths(input_dir, args.recursive)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        if args.device == "cuda" and not torch.cuda.is_available():
            print("CUDA is not available on this machine. Falling back to CPU.", file=sys.stderr)
            device = torch.device("cpu")
        else:
            device = torch.device(args.device)

    print(f"Using device: {device}")

    try:
        model, categories, preprocess = load_model(device)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Failed to load pretrained model: {exc}", file=sys.stderr)
        sys.exit(1)

    results = run_inference(model, preprocess, categories, image_paths, device, top_k)

    if not results:
        print("No predictions were generated (all images may have failed to load).", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    write_predictions(results, output_path, top_k)


if __name__ == "__main__":
    main()
