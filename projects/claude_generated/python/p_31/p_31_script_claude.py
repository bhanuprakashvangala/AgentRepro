#!/usr/bin/env python3
"""
File Compression Tool
Supports multiple compression formats: zip, tar.gz, tar.bz2
"""

import os
import sys
import zipfile
import tarfile
import gzip
import shutil
import argparse
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm


class FileCompressor:
    """Handle file compression operations with progress tracking."""

    SUPPORTED_FORMATS = ['zip', 'tar.gz', 'tar.bz2', 'gz']

    def __init__(self, compression_level: int = 6):
        """
        Initialize the compressor.

        Args:
            compression_level: Compression level (1-9, where 9 is maximum compression)
        """
        if not 1 <= compression_level <= 9:
            raise ValueError("Compression level must be between 1 and 9")
        self.compression_level = compression_level

    def get_total_size(self, paths: List[str]) -> int:
        """Calculate total size of files to be compressed."""
        total_size = 0
        for path in paths:
            if os.path.isfile(path):
                total_size += os.path.getsize(path)
            elif os.path.isdir(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
        return total_size

    def compress_zip(self, sources: List[str], output: str) -> None:
        """
        Compress files/directories to ZIP format.

        Args:
            sources: List of file/directory paths to compress
            output: Output ZIP file path
        """
        total_size = self.get_total_size(sources)

        # Map compression level (1-9) to zipfile constants
        if self.compression_level <= 3:
            compression_type = zipfile.ZIP_STORED
        else:
            compression_type = zipfile.ZIP_DEFLATED

        with zipfile.ZipFile(output, 'w', compression_type,
                            compresslevel=self.compression_level) as zipf:
            with tqdm(total=total_size, unit='B', unit_scale=True,
                     desc="Compressing to ZIP") as pbar:
                for source in sources:
                    if os.path.isfile(source):
                        zipf.write(source, os.path.basename(source))
                        pbar.update(os.path.getsize(source))
                    elif os.path.isdir(source):
                        self._add_directory_to_zip(zipf, source, pbar)

        print(f"\n✓ Created: {output} ({self._format_size(os.path.getsize(output))})")
        print(f"  Compression ratio: {self._get_compression_ratio(total_size, output):.1f}%")

    def compress_tar_gz(self, sources: List[str], output: str) -> None:
        """
        Compress files/directories to TAR.GZ format.

        Args:
            sources: List of file/directory paths to compress
            output: Output TAR.GZ file path
        """
        total_size = self.get_total_size(sources)

        with tarfile.open(output, f'w:gz', compresslevel=self.compression_level) as tar:
            with tqdm(total=total_size, unit='B', unit_scale=True,
                     desc="Compressing to TAR.GZ") as pbar:
                for source in sources:
                    arcname = os.path.basename(source)
                    if os.path.isfile(source):
                        tar.add(source, arcname=arcname)
                        pbar.update(os.path.getsize(source))
                    elif os.path.isdir(source):
                        self._add_directory_to_tar(tar, source, arcname, pbar)

        print(f"\n✓ Created: {output} ({self._format_size(os.path.getsize(output))})")
        print(f"  Compression ratio: {self._get_compression_ratio(total_size, output):.1f}%")

    def compress_tar_bz2(self, sources: List[str], output: str) -> None:
        """
        Compress files/directories to TAR.BZ2 format.

        Args:
            sources: List of file/directory paths to compress
            output: Output TAR.BZ2 file path
        """
        total_size = self.get_total_size(sources)

        with tarfile.open(output, f'w:bz2', compresslevel=self.compression_level) as tar:
            with tqdm(total=total_size, unit='B', unit_scale=True,
                     desc="Compressing to TAR.BZ2") as pbar:
                for source in sources:
                    arcname = os.path.basename(source)
                    if os.path.isfile(source):
                        tar.add(source, arcname=arcname)
                        pbar.update(os.path.getsize(source))
                    elif os.path.isdir(source):
                        self._add_directory_to_tar(tar, source, arcname, pbar)

        print(f"\n✓ Created: {output} ({self._format_size(os.path.getsize(output))})")
        print(f"  Compression ratio: {self._get_compression_ratio(total_size, output):.1f}%")

    def compress_gz(self, source: str, output: str) -> None:
        """
        Compress a single file to GZ format.

        Args:
            source: Source file path
            output: Output GZ file path
        """
        if not os.path.isfile(source):
            raise ValueError("GZ compression only supports single files")

        file_size = os.path.getsize(source)

        with open(source, 'rb') as f_in:
            with gzip.open(output, 'wb', compresslevel=self.compression_level) as f_out:
                with tqdm(total=file_size, unit='B', unit_scale=True,
                         desc="Compressing to GZ") as pbar:
                    chunk_size = 1024 * 1024  # 1MB chunks
                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        pbar.update(len(chunk))

        print(f"\n✓ Created: {output} ({self._format_size(os.path.getsize(output))})")
        print(f"  Compression ratio: {self._get_compression_ratio(file_size, output):.1f}%")

    def compress(self, sources: List[str], output: str, format: str) -> None:
        """
        Compress files/directories to the specified format.

        Args:
            sources: List of file/directory paths to compress
            output: Output file path
            format: Compression format (zip, tar.gz, tar.bz2, gz)
        """
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}")

        # Validate sources
        for source in sources:
            if not os.path.exists(source):
                raise FileNotFoundError(f"Source not found: {source}")

        # Ensure output has correct extension
        if not output.endswith(f'.{format}'):
            output = f'{output}.{format}'

        print(f"Compression level: {self.compression_level}/9")
        print(f"Format: {format.upper()}")
        print(f"Sources: {', '.join(sources)}")
        print(f"Output: {output}\n")

        if format == 'zip':
            self.compress_zip(sources, output)
        elif format == 'tar.gz':
            self.compress_tar_gz(sources, output)
        elif format == 'tar.bz2':
            self.compress_tar_bz2(sources, output)
        elif format == 'gz':
            if len(sources) > 1:
                raise ValueError("GZ format only supports single file compression")
            self.compress_gz(sources[0], output)

    def _add_directory_to_zip(self, zipf: zipfile.ZipFile, directory: str,
                             pbar: tqdm) -> None:
        """Add directory contents to ZIP file with progress tracking."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(directory))
                zipf.write(file_path, arcname)
                pbar.update(os.path.getsize(file_path))

    def _add_directory_to_tar(self, tar: tarfile.TarFile, directory: str,
                             arcname: str, pbar: tqdm) -> None:
        """Add directory contents to TAR file with progress tracking."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.join(arcname, os.path.relpath(file_path, directory))
                tar.add(file_path, arcname=arc_path)
                pbar.update(os.path.getsize(file_path))

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    @staticmethod
    def _get_compression_ratio(original_size: int, compressed_file: str) -> float:
        """Calculate compression ratio as percentage."""
        compressed_size = os.path.getsize(compressed_file)
        if original_size == 0:
            return 0.0
        return (1 - compressed_size / original_size) * 100


def main():
    """Main entry point for the compression tool."""
    parser = argparse.ArgumentParser(
        description='File Compression Tool - Support for multiple formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compress a single file to ZIP
  python file_compressor.py myfile.txt -o archive.zip -f zip

  # Compress multiple files/directories to TAR.GZ
  python file_compressor.py file1.txt dir1/ dir2/ -o backup.tar.gz -f tar.gz

  # Compress with maximum compression level
  python file_compressor.py large_file.log -o compressed.gz -f gz -l 9

  # Compress directory to TAR.BZ2 with medium compression
  python file_compressor.py ./project -o project_backup.tar.bz2 -f tar.bz2 -l 6
        """
    )

    parser.add_argument(
        'sources',
        nargs='+',
        help='File(s) or directory(ies) to compress'
    )

    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Output archive file path'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['zip', 'tar.gz', 'tar.bz2', 'gz'],
        required=True,
        help='Compression format'
    )

    parser.add_argument(
        '-l', '--level',
        type=int,
        default=6,
        choices=range(1, 10),
        metavar='1-9',
        help='Compression level (1=fastest, 9=maximum compression, default=6)'
    )

    args = parser.parse_args()

    try:
        compressor = FileCompressor(compression_level=args.level)
        compressor.compress(args.sources, args.output, args.format)
        return 0
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
