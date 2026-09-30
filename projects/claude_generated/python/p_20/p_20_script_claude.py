#!/usr/bin/env python3
"""
File Deduplication Tool
Finds and removes duplicate files based on content hash comparison.
"""

import hashlib
import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set
import json
from datetime import datetime


class FileDeduplicator:
    """Main class for file deduplication operations."""

    def __init__(self, hash_algorithm: str = 'sha256', chunk_size: int = 8192):
        """
        Initialize the deduplicator.

        Args:
            hash_algorithm: Hash algorithm to use ('md5' or 'sha256')
            chunk_size: Size of chunks for reading files (bytes)
        """
        self.hash_algorithm = hash_algorithm.lower()
        self.chunk_size = chunk_size
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.processed_files = 0
        self.total_size_scanned = 0

    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal hash string
        """
        if self.hash_algorithm == 'md5':
            hasher = hashlib.md5()
        elif self.hash_algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unsupported hash algorithm: {self.hash_algorithm}")

        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def scan_directory(self, directory: Path, exclude_patterns: Set[str] = None) -> None:
        """
        Recursively scan directory and build hash map.

        Args:
            directory: Root directory to scan
            exclude_patterns: Set of patterns to exclude (e.g., {'.git', '__pycache__'})
        """
        exclude_patterns = exclude_patterns or set()

        print(f"Scanning directory: {directory}")

        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for filename in files:
                file_path = Path(root) / filename

                # Skip if file matches exclude pattern
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue

                try:
                    # Skip empty files
                    file_size = file_path.stat().st_size
                    if file_size == 0:
                        continue

                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        self.file_hashes[file_hash].append(file_path)
                        self.processed_files += 1
                        self.total_size_scanned += file_size

                        if self.processed_files % 100 == 0:
                            print(f"Processed {self.processed_files} files...", end='\r')

                except (IOError, OSError) as e:
                    print(f"\nError accessing file {file_path}: {e}")

        print(f"\nScan complete: {self.processed_files} files processed")

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """
        Find all duplicate files.

        Returns:
            Dictionary mapping hash to list of duplicate file paths
        """
        duplicates = {
            file_hash: paths
            for file_hash, paths in self.file_hashes.items()
            if len(paths) > 1
        }
        return duplicates

    def calculate_duplicate_size(self, duplicates: Dict[str, List[Path]]) -> int:
        """
        Calculate total size that can be freed by removing duplicates.

        Args:
            duplicates: Dictionary of duplicate files

        Returns:
            Total size in bytes
        """
        total_waste = 0
        for paths in duplicates.values():
            # Keep one copy, count the rest as waste
            file_size = paths[0].stat().st_size
            total_waste += file_size * (len(paths) - 1)
        return total_waste

    def generate_report(self, duplicates: Dict[str, List[Path]], output_file: Path = None) -> str:
        """
        Generate a detailed report of duplicates.

        Args:
            duplicates: Dictionary of duplicate files
            output_file: Optional file path to save report

        Returns:
            Report string
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FILE DEDUPLICATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Hash Algorithm: {self.hash_algorithm.upper()}")
        report_lines.append(f"Total Files Scanned: {self.processed_files}")
        report_lines.append(f"Total Size Scanned: {self._format_size(self.total_size_scanned)}")
        report_lines.append("")

        if not duplicates:
            report_lines.append("No duplicate files found!")
        else:
            duplicate_sets = len(duplicates)
            total_duplicate_files = sum(len(paths) - 1 for paths in duplicates.values())
            total_waste = self.calculate_duplicate_size(duplicates)

            report_lines.append(f"Duplicate Sets Found: {duplicate_sets}")
            report_lines.append(f"Total Duplicate Files: {total_duplicate_files}")
            report_lines.append(f"Space that can be freed: {self._format_size(total_waste)}")
            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("DUPLICATE FILE DETAILS")
            report_lines.append("=" * 80)

            for idx, (file_hash, paths) in enumerate(duplicates.items(), 1):
                file_size = paths[0].stat().st_size
                report_lines.append(f"\nSet {idx}: {len(paths)} copies - {self._format_size(file_size)} each")
                report_lines.append(f"Hash: {file_hash}")
                for path in paths:
                    report_lines.append(f"  - {path}")

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report, encoding='utf-8')
            print(f"\nReport saved to: {output_file}")

        return report

    def remove_duplicates(self, duplicates: Dict[str, List[Path]],
                         backup_dir: Path = None,
                         keep_strategy: str = 'first',
                         dry_run: bool = False) -> Dict[str, any]:
        """
        Remove duplicate files with optional backup.

        Args:
            duplicates: Dictionary of duplicate files
            backup_dir: Directory to move duplicates to (if None, files are deleted)
            keep_strategy: Which file to keep ('first', 'last', 'shortest_path', 'longest_path')
            dry_run: If True, only simulate removal

        Returns:
            Dictionary with removal statistics
        """
        if backup_dir and not dry_run:
            backup_dir.mkdir(parents=True, exist_ok=True)

        removed_count = 0
        freed_space = 0
        errors = []

        for file_hash, paths in duplicates.items():
            # Determine which file to keep
            if keep_strategy == 'first':
                keep_file = paths[0]
                remove_files = paths[1:]
            elif keep_strategy == 'last':
                keep_file = paths[-1]
                remove_files = paths[:-1]
            elif keep_strategy == 'shortest_path':
                keep_file = min(paths, key=lambda p: len(str(p)))
                remove_files = [p for p in paths if p != keep_file]
            elif keep_strategy == 'longest_path':
                keep_file = max(paths, key=lambda p: len(str(p)))
                remove_files = [p for p in paths if p != keep_file]
            else:
                raise ValueError(f"Unknown keep strategy: {keep_strategy}")

            print(f"\nKeeping: {keep_file}")

            for file_path in remove_files:
                try:
                    file_size = file_path.stat().st_size

                    if dry_run:
                        print(f"[DRY RUN] Would remove: {file_path}")
                    else:
                        if backup_dir:
                            # Move to backup with preserved structure
                            backup_path = backup_dir / file_hash[:8] / file_path.name
                            backup_path.parent.mkdir(parents=True, exist_ok=True)

                            # Handle name conflicts in backup
                            counter = 1
                            original_backup_path = backup_path
                            while backup_path.exists():
                                backup_path = original_backup_path.parent / f"{original_backup_path.stem}_{counter}{original_backup_path.suffix}"
                                counter += 1

                            shutil.move(str(file_path), str(backup_path))
                            print(f"Moved to backup: {file_path} -> {backup_path}")
                        else:
                            file_path.unlink()
                            print(f"Deleted: {file_path}")

                    removed_count += 1
                    freed_space += file_size

                except (IOError, OSError) as e:
                    error_msg = f"Error removing {file_path}: {e}"
                    print(error_msg)
                    errors.append(error_msg)

        return {
            'removed_count': removed_count,
            'freed_space': freed_space,
            'errors': errors,
            'dry_run': dry_run
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='File Deduplication Tool - Find and remove duplicate files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan directory and generate report
  python deduplicate.py /path/to/directory

  # Remove duplicates with backup
  python deduplicate.py /path/to/directory --remove --backup ./backup

  # Remove duplicates permanently (careful!)
  python deduplicate.py /path/to/directory --remove --no-backup

  # Dry run to see what would be removed
  python deduplicate.py /path/to/directory --remove --dry-run

  # Use MD5 instead of SHA256
  python deduplicate.py /path/to/directory --hash md5
        """
    )

    parser.add_argument(
        'directory',
        type=Path,
        help='Directory to scan for duplicates'
    )

    parser.add_argument(
        '--hash',
        choices=['md5', 'sha256'],
        default='sha256',
        help='Hash algorithm to use (default: sha256)'
    )

    parser.add_argument(
        '--exclude',
        nargs='+',
        default=['.git', '__pycache__', 'node_modules', '.venv'],
        help='Patterns to exclude from scan (default: .git __pycache__ node_modules .venv)'
    )

    parser.add_argument(
        '--report',
        type=Path,
        help='Save report to file'
    )

    parser.add_argument(
        '--remove',
        action='store_true',
        help='Remove duplicate files (use with caution!)'
    )

    parser.add_argument(
        '--backup',
        type=Path,
        help='Backup directory for removed duplicates (recommended with --remove)'
    )

    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Delete duplicates without backup (DANGEROUS!)'
    )

    parser.add_argument(
        '--keep',
        choices=['first', 'last', 'shortest_path', 'longest_path'],
        default='first',
        help='Strategy for which file to keep (default: first)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate removal without actually deleting files'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.directory.exists():
        print(f"Error: Directory does not exist: {args.directory}")
        return 1

    if not args.directory.is_dir():
        print(f"Error: Path is not a directory: {args.directory}")
        return 1

    if args.remove and not args.backup and not args.no_backup and not args.dry_run:
        print("Error: Use --backup <directory> to backup duplicates, or --no-backup to delete without backup")
        print("       Or use --dry-run to simulate the operation first")
        return 1

    # Initialize deduplicator
    deduplicator = FileDeduplicator(hash_algorithm=args.hash)

    # Scan directory
    print(f"Starting scan of: {args.directory.absolute()}")
    deduplicator.scan_directory(args.directory, exclude_patterns=set(args.exclude))

    # Find duplicates
    duplicates = deduplicator.find_duplicates()

    # Generate and display report
    print("\n")
    report = deduplicator.generate_report(duplicates, output_file=args.report)
    print(report)

    # Remove duplicates if requested
    if args.remove and duplicates:
        print("\n" + "=" * 80)
        print("REMOVING DUPLICATES")
        print("=" * 80)

        backup_dir = args.backup if not args.no_backup else None

        if args.dry_run:
            print("\n*** DRY RUN MODE - No files will be modified ***\n")
        elif not backup_dir:
            print("\n*** WARNING: Files will be permanently deleted! ***\n")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != 'yes':
                print("Operation cancelled.")
                return 0

        stats = deduplicator.remove_duplicates(
            duplicates,
            backup_dir=backup_dir,
            keep_strategy=args.keep,
            dry_run=args.dry_run
        )

        print("\n" + "=" * 80)
        print("REMOVAL SUMMARY")
        print("=" * 80)
        print(f"Files removed: {stats['removed_count']}")
        print(f"Space freed: {FileDeduplicator._format_size(stats['freed_space'])}")
        if stats['errors']:
            print(f"Errors encountered: {len(stats['errors'])}")
        if stats['dry_run']:
            print("\n*** This was a DRY RUN - no files were actually modified ***")

    return 0


if __name__ == '__main__':
    exit(main())
