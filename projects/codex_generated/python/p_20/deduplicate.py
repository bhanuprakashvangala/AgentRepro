#!/usr/bin/env python3
"""Find duplicate files by content hash and optionally move them to a backup location."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SUPPORTED_HASHES = {"md5": hashlib.md5, "sha256": hashlib.sha256}
BUFFER_SIZE = 1024 * 1024  # 1 MB


@dataclass
class FileEntry:
    path: Path
    size: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="File deduplication tool")
    parser.add_argument("--paths", nargs="+", help="Directories to scan for duplicates", required=True)
    parser.add_argument(
        "--hash",
        choices=SUPPORTED_HASHES.keys(),
        default="sha256",
        help="Hash algorithm to use (default: sha256)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        help="Minimum file size in bytes to consider (default: 1)",
    )
    parser.add_argument(
        "--backup-dir",
        help="Directory to move duplicate files into instead of deleting",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Remove duplicates (moves to backup if provided)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without deleting/moving files",
    )
    return parser.parse_args()


def iter_files(paths: Iterable[str], min_size: int) -> Iterable[FileEntry]:
    for root in paths:
        root_path = Path(root)
        if not root_path.exists():
            print(f"Warning: path not found: {root_path}", file=sys.stderr)
            continue
        for path in root_path.rglob("*"):
            if path.is_file():
                size = path.stat().st_size
                if size >= min_size:
                    yield FileEntry(path=path, size=size)


def hash_file(path: Path, hash_name: str) -> str:
    hasher = SUPPORTED_HASHES[hash_name]()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(BUFFER_SIZE)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def group_by_hash(files: Iterable[FileEntry], hash_name: str) -> Dict[str, List[FileEntry]]:
    buckets: Dict[str, List[FileEntry]] = {}
    for entry in files:
        try:
            digest = hash_file(entry.path, hash_name)
        except (OSError, PermissionError) as exc:
            print(f"Error hashing {entry.path}: {exc}", file=sys.stderr)
            continue
        buckets.setdefault(digest, []).append(entry)
    return buckets


def print_duplicates(duplicates: Dict[str, List[FileEntry]]) -> None:
    for digest, entries in duplicates.items():
        if len(entries) <= 1:
            continue
        print(f"Hash {digest} ({entries[0].size} bytes):")
        for entry in entries:
            print(f"  {entry.path}")


def ensure_backup_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def move_file(src: Path, dst_dir: Path, dry_run: bool) -> None:
    relative = src.name
    target = dst_dir / relative
    counter = 1
    while target.exists():
        stem = src.stem
        suffix = src.suffix
        target = dst_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    if dry_run:
        print(f"Would move {src} -> {target}")
        return
    ensure_backup_dir(dst_dir)
    shutil.move(str(src), str(target))
    print(f"Moved {src} -> {target}")


def delete_file(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"Would delete {path}")
        return
    path.unlink()
    print(f"Deleted {path}")


def handle_duplicates(
    duplicates: Dict[str, List[FileEntry]],
    *,
    delete: bool,
    backup_dir: Path | None,
    dry_run: bool,
) -> Tuple[int, int]:
    files_removed = 0
    bytes_freed = 0
    for digest, entries in duplicates.items():
        if len(entries) <= 1:
            continue
        keep = entries[0]
        duplicates_to_remove = entries[1:]
        for dup in duplicates_to_remove:
            if delete:
                if backup_dir:
                    move_file(dup.path, backup_dir, dry_run)
                else:
                    delete_file(dup.path, dry_run)
            else:
                print(f"Duplicate detected (keeping {keep.path}): {dup.path}")
            files_removed += 1 if delete and not dry_run else 0
            bytes_freed += dup.size if delete and not dry_run else 0
    return files_removed, bytes_freed


def main() -> None:
    args = parse_args()
    backup_dir = Path(args.backup_dir) if args.backup_dir else None
    if backup_dir and args.delete and not args.dry_run:
        ensure_backup_dir(backup_dir)

    files = list(iter_files(args.paths, args.min_size))
    print(f"Scanned {len(files)} files meeting size >= {args.min_size} bytes")

    buckets = group_by_hash(files, args.hash)
    duplicates = {digest: entries for digest, entries in buckets.items() if len(entries) > 1}

    if not duplicates:
        print("No duplicates found.")
        return

    print_duplicates(duplicates)
    files_removed, bytes_freed = handle_duplicates(
        duplicates,
        delete=args.delete,
        backup_dir=backup_dir,
        dry_run=args.dry_run,
    )

    if args.delete:
        action = "would be" if args.dry_run else ""
        print(
            f"Total duplicates {action} removed: {files_removed} files" \
            f" freeing {bytes_freed} bytes"
        )
    else:
        print("Use --delete to remove or move duplicates")


if __name__ == "__main__":
    main()
