#!/usr/bin/env python3
"""File compression utility supporting zip, tar.gz, and tar.bz2 with progress."""

from __future__ import annotations

import argparse
import os
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterable, List

CHUNK_SIZE = 1024 * 1024  # 1 MB
SUPPORTED_FORMATS = {"zip", "tar.gz", "tar.bz2"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compress files/directories into various archive formats")
    parser.add_argument("--input", nargs="+", required=True, help="Files or directories to compress")
    parser.add_argument("--output", required=True, help="Output archive path (extension determines format)")
    parser.add_argument(
        "--compression-level",
        type=int,
        default=None,
        help="Compression level (0-9 for gzip/bzip2, 0-9 for zip)",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing archive")
    return parser.parse_args()


def resolve_format(output_path: Path) -> str:
    lower = output_path.name.lower()
    for fmt in SUPPORTED_FORMATS:
        if lower.endswith(fmt):
            return fmt
    raise ValueError("Unsupported output format. Use .zip, .tar.gz, or .tar.bz2")


def gather_files(paths: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for item in paths:
        path = Path(item)
        if not path.exists():
            print(f"Warning: path not found {path}", file=sys.stderr)
            continue
        if path.is_file():
            files.append(path)
        else:
            files.extend(p for p in path.rglob("*") if p.is_file())
    return files


def get_total_size(files: Iterable[Path]) -> int:
    return sum(p.stat().st_size for p in files)


def print_progress(processed: int, total: int) -> None:
    if total <= 0:
        return
    percent = processed / total * 100
    bar_length = 30
    filled = int(bar_length * percent / 100)
    bar = "#" * filled + "-" * (bar_length - filled)
    sys.stderr.write(f"\r[{bar}] {percent:6.2f}%")
    sys.stderr.flush()


def finalize_progress() -> None:
    sys.stderr.write("\r[##############################] 100.00%\n")
    sys.stderr.flush()


def compress_zip(files: List[Path], output_path: Path, compression_level: int | None) -> None:
    compression = zipfile.ZIP_DEFLATED
    zip_kwargs = {}
    if compression_level is not None:
        if compression_level == 0:
            compression = zipfile.ZIP_STORED
        else:
            zip_kwargs["compresslevel"] = max(0, min(compression_level, 9))

    with zipfile.ZipFile(output_path, mode="w", compression=compression, **zip_kwargs) as zf:
        total = get_total_size(files)
        processed = 0
        for file_path in files:
            arcname = file_path.relative_to(Path.cwd()) if file_path.is_absolute() else file_path
            zf.write(file_path, arcname=str(arcname))
            processed += file_path.stat().st_size
            print_progress(processed, total)
    finalize_progress()


def compress_tar(files: List[Path], output_path: Path, mode: str, compression_level: int | None) -> None:
    tar_kwargs = {}
    if "gz" in mode and compression_level is not None:
        tar_kwargs["compresslevel"] = max(0, min(compression_level, 9))
    if "bz2" in mode and compression_level is not None:
        tar_kwargs["compresslevel"] = max(1, min(compression_level, 9))

    total = get_total_size(files)
    processed = 0
    with tarfile.open(output_path, mode, **tar_kwargs) as tar:
        for file_path in files:
            arcname = file_path.relative_to(Path.cwd()) if file_path.is_absolute() else file_path
            tar.add(file_path, arcname=str(arcname))
            processed += file_path.stat().st_size
            print_progress(processed, total)
    finalize_progress()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        print("Error: output file exists. Use --overwrite to replace.", file=sys.stderr)
        sys.exit(1)

    fmt = resolve_format(output_path)
    files = gather_files(args.input)
    if not files:
        print("No input files to compress.", file=sys.stderr)
        sys.exit(1)

    if fmt == "zip":
        compress_zip(files, output_path, args.compression_level)
    elif fmt == "tar.gz":
        mode = "w:gz"
        compress_tar(files, output_path, mode, args.compression_level)
    elif fmt == "tar.bz2":
        mode = "w:bz2"
        compress_tar(files, output_path, mode, args.compression_level)
    else:
        raise ValueError("Unsupported format")

    print(f"Archive created: {output_path}")


if __name__ == "__main__":
    main()
