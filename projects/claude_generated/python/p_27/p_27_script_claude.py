import cv2
import os
import sys
import argparse
from pathlib import Path


def detect_faces(image_path, output_path=None, scale_factor=1.1, min_neighbors=5, min_size=(30, 30)):
    """
    Detect faces in an image using Haar Cascade classifier.

    Args:
        image_path: Path to input image
        output_path: Path to save output image (optional)
        scale_factor: Parameter specifying how much the image size is reduced at each image scale
        min_neighbors: Parameter specifying how many neighbors each candidate rectangle should have
        min_size: Minimum possible object size

    Returns:
        Number of faces detected
    """
    # Load the cascade classifier
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        raise IOError("Failed to load Haar Cascade classifier")

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise IOError(f"Failed to load image: {image_path}")

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=scale_factor,
        minNeighbors=min_neighbors,
        minSize=min_size,
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Save or display the result
    if output_path:
        cv2.imwrite(output_path, image)
        print(f"Saved result to: {output_path}")

    return len(faces), image


def batch_process(input_dir, output_dir=None, scale_factor=1.1, min_neighbors=5, min_size=(30, 30)):
    """
    Process multiple images in a directory.

    Args:
        input_dir: Directory containing input images
        output_dir: Directory to save output images (optional)
        scale_factor: Parameter for face detection
        min_neighbors: Parameter for face detection
        min_size: Minimum face size

    Returns:
        Dictionary with processing results
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Create output directory if specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}

    # Process all images
    results = {}
    image_files = [f for f in input_path.iterdir()
                   if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"No images found in {input_dir}")
        return results

    print(f"Processing {len(image_files)} images...")

    for img_file in image_files:
        try:
            output_file = None
            if output_dir:
                output_file = str(Path(output_dir) / f"detected_{img_file.name}")

            num_faces, _ = detect_faces(
                str(img_file),
                output_file,
                scale_factor,
                min_neighbors,
                min_size
            )

            results[img_file.name] = {
                'status': 'success',
                'faces_detected': num_faces
            }
            print(f"✓ {img_file.name}: {num_faces} face(s) detected")

        except Exception as e:
            results[img_file.name] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"✗ {img_file.name}: Error - {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Face Detection using OpenCV Haar Cascades',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single image:
    python face_detection.py -i photo.jpg -o output.jpg

  Batch processing:
    python face_detection.py -d ./images -o ./results

  Custom detection parameters:
    python face_detection.py -i photo.jpg -o output.jpg --scale 1.2 --neighbors 3
        """
    )

    parser.add_argument('-i', '--image', help='Path to input image')
    parser.add_argument('-d', '--directory', help='Path to directory containing images')
    parser.add_argument('-o', '--output', help='Path to output image/directory')
    parser.add_argument('--scale', type=float, default=1.1,
                        help='Scale factor for detection (default: 1.1)')
    parser.add_argument('--neighbors', type=int, default=5,
                        help='Minimum neighbors for detection (default: 5)')
    parser.add_argument('--min-width', type=int, default=30,
                        help='Minimum face width in pixels (default: 30)')
    parser.add_argument('--min-height', type=int, default=30,
                        help='Minimum face height in pixels (default: 30)')

    args = parser.parse_args()

    # Validate arguments
    if not args.image and not args.directory:
        parser.error("Either --image or --directory must be specified")

    if args.image and args.directory:
        parser.error("Cannot specify both --image and --directory")

    min_size = (args.min_width, args.min_height)

    try:
        if args.image:
            # Single image processing
            num_faces, _ = detect_faces(
                args.image,
                args.output,
                args.scale,
                args.neighbors,
                min_size
            )
            print(f"\nDetected {num_faces} face(s) in {args.image}")

        else:
            # Batch processing
            results = batch_process(
                args.directory,
                args.output,
                args.scale,
                args.neighbors,
                min_size
            )

            # Summary
            total = len(results)
            successful = sum(1 for r in results.values() if r['status'] == 'success')
            total_faces = sum(r.get('faces_detected', 0) for r in results.values()
                            if r['status'] == 'success')

            print(f"\n{'='*50}")
            print(f"Summary:")
            print(f"  Total images: {total}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {total - successful}")
            print(f"  Total faces detected: {total_faces}")
            print(f"{'='*50}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
