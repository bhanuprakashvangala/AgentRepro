#!/usr/bin/env python3
"""Batch image resize and optimization tool using Pillow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resize and optimize images in batch")
    parser.add_argument("--input", nargs="+", required=True, help="Image files or directories to process")
    parser.add_argument("--output-dir", required=True, help="Directory for optimized images")
    parser.add_argument("--width", type=int, help="Target width in pixels")
    parser.add_argument("--height", type=int, help="Target height in pixels")
    parser.add_argument(
        "--max-dimension",
        type=int,
        help="Maximum dimension (longest side) in pixels",
    )
    parser.add_argument(
        "--no-keep-aspect",
        action="store_true",
        help="Do not preserve aspect ratio (exact width/height)",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="JPEG/WebP quality (default 85)",
    )
    parser.add_argument(
        "--format",
        choices=["keep", "jpeg", "png", "webp"],
        default="keep",
        help="Output format (default keep original)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files in output directory",
    )
    return parser.parse_args()


def collect_images(paths: Iterable[str]) -> List[Path]:
    images: List[Path] = []
    for entry in paths:
        path = Path(entry)
        if not path.exists():
            print(f"Warning: {path} does not exist", file=sys.stderr)
            continue
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            images.append(path)
        elif path.is_dir():
            images.extend(
                p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
            )
    return images


def calculate_size(img: Image.Image, width: int | None, height: int | None, max_dim: int | None, keep_aspect: bool) -> tuple[int, int]:
    orig_width, orig_height = img.size

    if not keep_aspect:
        new_width = width or orig_width
        new_height = height or orig_height
        return max(1, new_width), max(1, new_height)

    if max_dim:
        ratio = min(max_dim / orig_width, max_dim / orig_height)
        if ratio >= 1:
            return orig_width, orig_height
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
        return max(1, new_width), max(1, new_height)

    if width and height:
        ratio = min(width / orig_width, height / orig_height)
        new_width = int(orig_width * ratio)
        new_height = int(orig_height * ratio)
        return max(1, new_width), max(1, new_height)

    if width:
        ratio = width / orig_width
        return max(1, width), max(1, int(orig_height * ratio))

    if height:
        ratio = height / orig_height
        return max(1, int(orig_width * ratio)), max(1, height)

    return orig_width, orig_height


def determine_output_path(image_path: Path, output_dir: Path, fmt: str) -> Path:
    if fmt == "keep":
        suffix = image_path.suffix
    elif fmt == "jpeg":
        suffix = ".jpg"
    elif fmt == "png":
        suffix = ".png"
    elif fmt == "webp":
        suffix = ".webp"
    else:
        suffix = image_path.suffix
    return output_dir / (image_path.stem + suffix)


def process_image(
    image_path: Path,
    output_path: Path,
    size: tuple[int, int],
    quality: int,
    fmt: str,
    overwrite: bool,
) -> None:
    if output_path.exists() and not overwrite:
        print(f"Skipping {image_path} (exists)")
        return

    with Image.open(image_path) as img:
        if size != img.size:
            img = img.resize(size, Image.LANCZOS)

        save_kwargs: dict = {"optimize": True}
        save_format = fmt.upper() if fmt != "keep" else img.format
        if save_format in {"JPEG", "JPG", "WEBP"}:
            save_kwargs["quality"] = max(1, min(quality, 100))
        if save_format == "JPEG":
            save_kwargs.setdefault("progressive", True)

        img.save(output_path, format=save_format, **save_kwargs)
        print(f"Saved {output_path} ({img.size[0]}x{img.size[1]})")


def main() -> None:
    args = parse_args()
    images = collect_images(args.input)
    if not images:
        print("No images found to process.")
        return

    if not (args.width or args.height or args.max_dimension):
        print("Error: specify --width, --height, or --max-dimension")
        sys.exit(1)

    keep_aspect = not args.no_keep_aspect
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in images:
        try:
            with Image.open(image_path) as img:
                size = calculate_size(img, args.width, args.height, args.max_dimension, keep_aspect)
            output_path = determine_output_path(image_path, output_dir, args.format)
            process_image(image_path, output_path, size, args.quality, args.format, args.overwrite)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error processing {image_path}: {exc}", file=sys.stderr)

    print("Batch processing complete.")


if __name__ == "__main__":
    main()
