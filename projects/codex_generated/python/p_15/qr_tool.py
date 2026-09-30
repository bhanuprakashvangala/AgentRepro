#!/usr/bin/env python3
"""QR code generator and reader supporting bulk operations."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

import cv2
import qrcode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QR code generator and reader")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Generate QR code images")
    gen_parser.add_argument("--data", nargs="*", help="Data strings to encode")
    gen_parser.add_argument(
        "--data-file",
        help="Text/CSV file containing data values (one per line or first column)",
    )
    gen_parser.add_argument(
        "--output-dir",
        default="qr_output",
        help="Directory to store generated QR codes",
    )
    gen_parser.add_argument(
        "--prefix",
        default="qr_",
        help="Filename prefix for generated images",
    )
    gen_parser.add_argument(
        "--image-format",
        default="png",
        choices=["png", "jpg", "bmp"],
        help="Image format for QR codes",
    )
    gen_parser.set_defaults(func=handle_generate)

    read_parser = subparsers.add_parser("read", help="Read QR codes from images")
    read_parser.add_argument("--input", required=True, help="File or directory containing images")
    read_parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search directories for images",
    )
    read_parser.add_argument(
        "--extensions",
        default="png,jpg,jpeg,bmp",
        help="Comma-separated list of image extensions to consider",
    )
    read_parser.add_argument(
        "--output",
        default="decoded.csv",
        help="CSV file to store decoded results",
    )
    read_parser.set_defaults(func=handle_read)

    return parser


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_data_sources(data_args: Sequence[str] | None, data_file: str | None) -> List[str]:
    collected: List[str] = []
    if data_args:
        collected.extend([item for item in data_args if item])

    if data_file:
        file_path = Path(data_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        with file_path.open("r", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            for row in reader:
                if not row:
                    continue
                collected.append(row[0].strip())
    if not collected:
        raise ValueError("No data provided. Use --data or --data-file.")
    return collected


def generate_qr_codes(data_items: Iterable[str], output_dir: Path, prefix: str, fmt: str) -> List[Path]:
    ensure_output_dir(output_dir)
    generated: List[Path] = []
    for index, value in enumerate(data_items, start=1):
        if not value:
            continue
        img = qrcode.make(value)
        filename = f"{prefix}{index:04d}.{fmt}"
        path = output_dir / filename
        img.save(path)
        generated.append(path)
        print(f"Generated {path} for data: {value}")
    return generated


def walk_image_paths(root: Path, extensions: Sequence[str], recursive: bool) -> List[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Input path not found: {root}")
    exts = {f".{ext.lower()}" for ext in extensions}
    if root.is_file():
        return [root] if root.suffix.lower() in exts else []
    if recursive:
        paths = [p for p in root.rglob("*") if p.suffix.lower() in exts]
    else:
        paths = [p for p in root.iterdir() if p.suffix.lower() in exts]
    return sorted(paths)


def decode_qr_code(image_path: Path) -> List[str]:
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Warning: unable to read image {image_path}", file=sys.stderr)
        return []
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecodeMulti(img)
    if points is None:
        single_data, single_points = detector.detectAndDecode(img)
        if single_points is not None and single_data:
            return [single_data]
        return []
    if isinstance(data, (tuple, list)):
        return [item for item in data if item]
    if data:
        return [data]
    return []


def handle_generate(args: argparse.Namespace) -> None:
    data_items = load_data_sources(args.data, args.data_file)
    output_dir = Path(args.output_dir)
    generate_qr_codes(data_items, output_dir, args.prefix, args.image_format)


def handle_read(args: argparse.Namespace) -> None:
    extensions = [ext.strip().lower() for ext in args.extensions.split(",") if ext.strip()]
    image_paths = walk_image_paths(Path(args.input), extensions, args.recursive)
    if not image_paths:
        print("No images found to decode.")
        return

    results: List[tuple[str, str]] = []
    for path in image_paths:
        decoded_values = decode_qr_code(path)
        if decoded_values:
            for value in decoded_values:
                results.append((str(path), value))
                print(f"Decoded from {path}: {value}")
        else:
            print(f"No QR code detected in {path}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["file", "data"])
        writer.writerows(results)
    print(f"Decoded results saved to {output_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
