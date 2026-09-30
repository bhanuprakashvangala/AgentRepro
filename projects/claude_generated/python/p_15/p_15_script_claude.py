"""
QR Code Generator and Reader Application
Supports single and bulk operations for generating and reading QR codes.
"""

import qrcode
import cv2
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import argparse


class QRCodeGenerator:
    """Generate QR codes with custom data."""

    def __init__(self, version: int = 1, box_size: int = 10, border: int = 4):
        """
        Initialize QR code generator.

        Args:
            version: QR code version (1-40), controls size
            box_size: Size of each box in pixels
            border: Border size in boxes
        """
        self.version = version
        self.box_size = box_size
        self.border = border

    def generate(self, data: str, output_path: str,
                 fill_color: str = "black",
                 back_color: str = "white") -> bool:
        """
        Generate a QR code from data.

        Args:
            data: Data to encode in QR code
            output_path: Path to save the QR code image
            fill_color: Color of QR code modules
            back_color: Background color

        Returns:
            True if successful, False otherwise
        """
        try:
            qr = qrcode.QRCode(
                version=self.version,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=self.box_size,
                border=self.border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            img.save(output_path)
            print(f"✓ Generated QR code: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error generating QR code: {e}")
            return False

    def generate_bulk(self, data_list: List[Tuple[str, str]]) -> int:
        """
        Generate multiple QR codes.

        Args:
            data_list: List of tuples (data, output_path)

        Returns:
            Number of successfully generated QR codes
        """
        success_count = 0
        for data, output_path in data_list:
            if self.generate(data, output_path):
                success_count += 1
        return success_count


class QRCodeReader:
    """Read QR codes from image files."""

    def __init__(self):
        """Initialize QR code reader."""
        self.detector = cv2.QRCodeDetector()

    def read(self, image_path: str) -> Optional[str]:
        """
        Read QR code from an image file.

        Args:
            image_path: Path to the image file

        Returns:
            Decoded data as string, or None if no QR code found
        """
        try:
            if not os.path.exists(image_path):
                print(f"✗ File not found: {image_path}")
                return None

            img = cv2.imread(image_path)
            if img is None:
                print(f"✗ Could not read image: {image_path}")
                return None

            data, bbox, _ = self.detector.detectAndDecode(img)

            if bbox is not None and data:
                print(f"✓ Read QR code from {image_path}")
                print(f"  Data: {data}")
                return data
            else:
                print(f"✗ No QR code found in: {image_path}")
                return None
        except Exception as e:
            print(f"✗ Error reading QR code from {image_path}: {e}")
            return None

    def read_bulk(self, image_paths: List[str]) -> List[Tuple[str, Optional[str]]]:
        """
        Read multiple QR codes from image files.

        Args:
            image_paths: List of paths to image files

        Returns:
            List of tuples (image_path, decoded_data)
        """
        results = []
        for image_path in image_paths:
            data = self.read(image_path)
            results.append((image_path, data))
        return results


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="QR Code Generator and Reader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single QR code
  python qr_app.py generate "Hello World" output.png

  # Generate multiple QR codes
  python qr_app.py generate-bulk data.txt output_dir/

  # Read a single QR code
  python qr_app.py read qrcode.png

  # Read multiple QR codes
  python qr_app.py read-bulk qr_images/
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate a QR code')
    gen_parser.add_argument('data', help='Data to encode')
    gen_parser.add_argument('output', help='Output image path')
    gen_parser.add_argument('--version', type=int, default=1, help='QR version (1-40)')
    gen_parser.add_argument('--box-size', type=int, default=10, help='Box size in pixels')
    gen_parser.add_argument('--border', type=int, default=4, help='Border size in boxes')

    # Generate bulk command
    gen_bulk_parser = subparsers.add_parser('generate-bulk',
                                            help='Generate multiple QR codes')
    gen_bulk_parser.add_argument('input_file',
                                 help='Text file with lines: data|output_path')
    gen_bulk_parser.add_argument('--version', type=int, default=1,
                                help='QR version (1-40)')
    gen_bulk_parser.add_argument('--box-size', type=int, default=10,
                                help='Box size in pixels')
    gen_bulk_parser.add_argument('--border', type=int, default=4,
                                help='Border size in boxes')

    # Read command
    read_parser = subparsers.add_parser('read', help='Read a QR code')
    read_parser.add_argument('image', help='Path to QR code image')

    # Read bulk command
    read_bulk_parser = subparsers.add_parser('read-bulk',
                                            help='Read multiple QR codes')
    read_bulk_parser.add_argument('input_dir', help='Directory containing QR code images')
    read_bulk_parser.add_argument('--pattern', default='*.png',
                                 help='File pattern (default: *.png)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute commands
    if args.command == 'generate':
        generator = QRCodeGenerator(
            version=args.version,
            box_size=args.box_size,
            border=args.border
        )
        generator.generate(args.data, args.output)

    elif args.command == 'generate-bulk':
        generator = QRCodeGenerator(
            version=args.version,
            box_size=args.box_size,
            border=args.border
        )

        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                data_list = []
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split('|')
                    if len(parts) != 2:
                        print(f"⚠ Skipping line {line_num}: Invalid format")
                        continue

                    data, output_path = parts[0].strip(), parts[1].strip()

                    # Create output directory if needed
                    output_dir = os.path.dirname(output_path)
                    if output_dir:
                        os.makedirs(output_dir, exist_ok=True)

                    data_list.append((data, output_path))

            if data_list:
                count = generator.generate_bulk(data_list)
                print(f"\n✓ Generated {count}/{len(data_list)} QR codes successfully")
            else:
                print("No valid entries found in input file")

        except FileNotFoundError:
            print(f"✗ Input file not found: {args.input_file}")
        except Exception as e:
            print(f"✗ Error: {e}")

    elif args.command == 'read':
        reader = QRCodeReader()
        reader.read(args.image)

    elif args.command == 'read-bulk':
        reader = QRCodeReader()

        input_path = Path(args.input_dir)
        if not input_path.exists():
            print(f"✗ Directory not found: {args.input_dir}")
            return

        image_files = list(input_path.glob(args.pattern))

        if not image_files:
            print(f"✗ No files matching '{args.pattern}' found in {args.input_dir}")
            return

        print(f"Processing {len(image_files)} files...\n")
        results = reader.read_bulk([str(f) for f in image_files])

        # Summary
        successful = sum(1 for _, data in results if data is not None)
        print(f"\n✓ Successfully read {successful}/{len(results)} QR codes")


if __name__ == "__main__":
    main()
