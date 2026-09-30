import os
import argparse
import requests
from PIL import Image

# --- Configuration ---
DEFAULT_OUTPUT_DIR = "processed_images"
DEMO_SOURCE_DIR = "source_images"
DEMO_IMAGES = {
    "landscape.jpg": "https://images.pexels.com/photos/3225517/pexels-photo-3225517.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260",
    "portrait.jpg": "https://images.pexels.com/photos/3573351/pexels-photo-3573351.png?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260"
}

def download_demo_images():
    """Downloads sample images for the demo."""
    if not os.path.exists(DEMO_SOURCE_DIR):
        os.makedirs(DEMO_SOURCE_DIR)
    
    for filename, url in DEMO_IMAGES.items():
        filepath = os.path.join(DEMO_SOURCE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[INFO] Downloading demo image: {filename}...")
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Could not download {filename}: {e}")
                return False
    return True

def process_image(input_path, output_dir, target_width, target_height, quality):
    """Resizes and optimizes a single image."""
    try:
        img = Image.open(input_path)
        original_size = img.size
        print(f"\nProcessing: {input_path} (Size: {original_size[0]}x{original_size[1]})")

        # --- Aspect Ratio Calculation ---
        # Use a copy for resizing to preserve original for format conversion if needed
        img_copy = img.copy()
        if target_width and target_height:
            # If both are specified, fit within the box while preserving aspect ratio
            size = (target_width, target_height)
            img_copy.thumbnail(size, Image.Resampling.LANCZOS)
        elif target_width:
            # If only width is specified, calculate height
            w_percent = (target_width / float(img_copy.size[0]))
            h_size = int((float(img_copy.size[1]) * float(w_percent)))
            img_copy = img_copy.resize((target_width, h_size), Image.Resampling.LANCZOS)
        elif target_height:
            # If only height is specified, calculate width
            h_percent = (target_height / float(img_copy.size[1]))
            w_size = int((float(img_copy.size[0]) * float(h_percent)))
            img_copy = img_copy.resize((w_size, target_height), Image.Resampling.LANCZOS)

        # --- Save with Optimization ---
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, filename)

        save_options = {'optimize': True}
        # The 'quality' option is primarily for JPEG
        if img.format == 'JPEG':
            save_options['quality'] = quality
        
        img_copy.save(output_path, **save_options)
        final_size = img_copy.size
        print(f" -> Saved to {output_path} (New Size: {final_size[0]}x{final_size[1]})")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {input_path}")
    except Exception as e:
        print(f"[ERROR] Could not process {input_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch resize and optimize images.")
    parser.add_argument("inputs", nargs='*', help="One or more input image files or directories.")
    parser.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"Directory to save processed images (default: {DEFAULT_OUTPUT_DIR}).")
    parser.add_argument("-w", "--width", type=int, help="Target width to resize to.")
    parser.add_argument("-ht", "--height", type=int, help="Target height to resize to.")
    parser.add_argument("-q", "--quality", type=int, default=85, choices=range(1, 96), metavar="[1-95]", help="JPEG quality for optimization (1-95, default: 85).")
    parser.add_argument("--demo", action="store_true", help="Run a demo with sample images.")
    args = parser.parse_args()

    if not args.width and not args.height and not args.demo:
        print("Error: You must specify at least --width or --height.")
        parser.print_help()
        exit()

    files_to_process = []
    if args.demo:
        if download_demo_images():
            args.inputs = [DEMO_SOURCE_DIR]
        else:
            exit()

    if not args.inputs:
        parser.print_help()
        exit()

    # Collect all image files from inputs
    for item in args.inputs:
        if os.path.isdir(item):
            for filename in os.listdir(item):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    files_to_process.append(os.path.join(item, filename))
        elif os.path.isfile(item):
            files_to_process.append(item)

    if not files_to_process:
        print("No image files found in the specified inputs.")
    else:
        print(f"Found {len(files_to_process)} image(s) to process.")
        for file_path in files_to_process:
            process_image(file_path, args.output_dir, args.width, args.height, args.quality)
        print("\n--- Batch Process Complete ---")
