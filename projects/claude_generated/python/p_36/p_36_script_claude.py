#!/usr/bin/env python3
"""
Image Resize and Optimization Tool
Batch resize and optimize images while maintaining quality
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageOps
import argparse


class ImageOptimizer:
    """Handle image resizing and optimization operations"""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}

    def __init__(self, quality: int = 85, maintain_aspect: bool = True):
        """
        Initialize the optimizer

        Args:
            quality: JPEG quality (1-100), higher = better quality
            maintain_aspect: Whether to preserve aspect ratio
        """
        self.quality = max(1, min(100, quality))
        self.maintain_aspect = maintain_aspect

    def resize_image(
        self,
        input_path: Path,
        output_path: Path,
        size: Tuple[int, int],
        optimize: bool = True
    ) -> bool:
        """
        Resize and optimize a single image

        Args:
            input_path: Source image path
            output_path: Destination image path
            size: Target size as (width, height)
            optimize: Whether to optimize file size

        Returns:
            True if successful, False otherwise
        """
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB for JPEG
                if img.mode in ('RGBA', 'LA', 'P') and output_path.suffix.lower() in {'.jpg', '.jpeg'}:
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background

                # Calculate new size
                if self.maintain_aspect:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                else:
                    img = img.resize(size, Image.Resampling.LANCZOS)

                # Auto-orient based on EXIF data
                img = ImageOps.exif_transpose(img)

                # Save with optimization
                save_kwargs = {
                    'optimize': optimize,
                    'quality': self.quality
                }

                # Format-specific options
                if output_path.suffix.lower() == '.png':
                    save_kwargs.pop('quality')
                    save_kwargs['compress_level'] = 9
                elif output_path.suffix.lower() == '.webp':
                    save_kwargs['method'] = 6

                img.save(output_path, **save_kwargs)

                # Report size reduction
                original_size = input_path.stat().st_size
                new_size = output_path.stat().st_size
                reduction = ((original_size - new_size) / original_size) * 100

                print(f"✓ {input_path.name} -> {output_path.name}")
                print(f"  {self._format_size(original_size)} -> {self._format_size(new_size)} "
                      f"({reduction:+.1f}%)")

                return True

        except Exception as e:
            print(f"✗ Error processing {input_path.name}: {e}", file=sys.stderr)
            return False

    def batch_resize(
        self,
        input_dir: Path,
        output_dir: Path,
        size: Tuple[int, int],
        recursive: bool = False
    ) -> Tuple[int, int]:
        """
        Batch resize all images in a directory

        Args:
            input_dir: Source directory
            output_dir: Destination directory
            size: Target size as (width, height)
            recursive: Whether to process subdirectories

        Returns:
            Tuple of (successful_count, failed_count)
        """
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find all images
        pattern = '**/*' if recursive else '*'
        image_files = [
            f for f in input_dir.glob(pattern)
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS
        ]

        if not image_files:
            print(f"No supported images found in {input_dir}")
            return 0, 0

        print(f"Found {len(image_files)} image(s) to process\n")

        successful = 0
        failed = 0

        for img_path in image_files:
            # Preserve directory structure if recursive
            if recursive:
                rel_path = img_path.relative_to(input_dir)
                output_path = output_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_path = output_dir / img_path.name

            if self.resize_image(img_path, output_path, size):
                successful += 1
            else:
                failed += 1

            print()  # Blank line between images

        return successful, failed

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def parse_size(size_str: str) -> Tuple[int, int]:
    """Parse size string like '800x600' to tuple (800, 600)"""
    try:
        width, height = size_str.lower().split('x')
        return int(width), int(height)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid size format: '{size_str}'. Use format like '800x600'"
        )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch resize and optimize images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resize all images in 'photos' to 800x600, save to 'output'
  %(prog)s photos output 800x600

  # High quality resize maintaining aspect ratio
  %(prog)s input output 1920x1080 -q 95

  # Resize without maintaining aspect ratio
  %(prog)s input output 500x500 --no-aspect

  # Process subdirectories recursively
  %(prog)s input output 1024x768 -r

Supported formats: JPG, PNG, WebP, BMP, TIFF
        """
    )

    parser.add_argument(
        'input_dir',
        type=Path,
        help='Input directory containing images'
    )
    parser.add_argument(
        'output_dir',
        type=Path,
        help='Output directory for resized images'
    )
    parser.add_argument(
        'size',
        type=parse_size,
        help='Target size in format WIDTHxHEIGHT (e.g., 800x600)'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='JPEG quality 1-100 (default: 85)'
    )
    parser.add_argument(
        '--no-aspect',
        action='store_true',
        help='Do not maintain aspect ratio (stretch to fit)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process subdirectories recursively'
    )
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='Disable file size optimization'
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input_dir.exists():
        print(f"Error: Input directory '{args.input_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    if not args.input_dir.is_dir():
        print(f"Error: '{args.input_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Initialize optimizer
    optimizer = ImageOptimizer(
        quality=args.quality,
        maintain_aspect=not args.no_aspect
    )

    # Process images
    print(f"Input:  {args.input_dir.absolute()}")
    print(f"Output: {args.output_dir.absolute()}")
    print(f"Size:   {args.size[0]}x{args.size[1]}")
    print(f"Aspect: {'Maintain' if not args.no_aspect else 'Stretch'}")
    print(f"Quality: {args.quality}")
    print("-" * 50)
    print()

    successful, failed = optimizer.batch_resize(
        args.input_dir,
        args.output_dir,
        args.size,
        recursive=args.recursive
    )

    # Summary
    print("=" * 50)
    print(f"Complete: {successful} successful, {failed} failed")

    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
