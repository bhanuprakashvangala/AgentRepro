#!/usr/bin/env python3
"""Batch face detection using OpenCV Haar cascades."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

import cv2

DEFAULT_CASCADE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect faces in images and draw bounding boxes")
    parser.add_argument("--inputs", nargs="+", help="Image files or directories to process")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where annotated images will be saved",
    )
    parser.add_argument(
        "--cascade",
        default=DEFAULT_CASCADE,
        help="Path to Haar cascade XML file (default: frontal face cascade bundled with OpenCV)",
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=1.1,
        help="Scale factor for face detection (default: 1.1)",
    )
    parser.add_argument(
        "--min-neighbors",
        type=int,
        default=5,
        help="Min neighbors for detection (default: 5)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=30,
        help="Minimum face size in pixels (default: 30)",
    )
    return parser.parse_args()


def collect_images(inputs: Iterable[str]) -> List[Path]:
    paths: List[Path] = []
    for entry in inputs:
        path = Path(entry)
        if not path.exists():
            print(f"Warning: input path not found: {path}", file=sys.stderr)
            continue
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                paths.append(path)
            else:
                print(f"Skipping unsupported file: {path}", file=sys.stderr)
        else:
            for image in path.rglob("*"):
                if image.is_file() and image.suffix.lower() in SUPPORTED_EXTENSIONS:
                    paths.append(image)
    return sorted(paths)


def load_classifier(cascade_path: str) -> cv2.CascadeClassifier:
    classifier = cv2.CascadeClassifier(cascade_path)
    if classifier.empty():
        raise RuntimeError(f"Failed to load Haar cascade from {cascade_path}")
    return classifier


def detect_faces(image_path: Path, classifier: cv2.CascadeClassifier, scale_factor: float, min_neighbors: int, min_size: int) -> cv2.Mat:
    image = cv2.imread(str(image_path))
    if image is None:
        raise RuntimeError(f"Unable to read image: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = classifier.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=(min_size, min_size),
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return image, len(faces)


def main() -> None:
    args = parse_args()
    images = collect_images(args.inputs)
    if not images:
        print("No valid images to process.")
        sys.exit(0)

    classifier = load_classifier(args.cascade)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    total_faces = 0
    for image_path in images:
        try:
            annotated, count = detect_faces(
                image_path,
                classifier,
                scale_factor=args.scale_factor,
                min_neighbors=args.min_neighbors,
                min_size=args.min_size,
            )
            total_faces += count
            output_path = output_dir / image_path.name
            cv2.imwrite(str(output_path), annotated)
            print(f"{image_path} -> {output_path} ({count} faces)")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error processing {image_path}: {exc}", file=sys.stderr)

    print(f"Finished. Processed {len(images)} images, detected {total_faces} faces.")


if __name__ == "__main__":
    main()
