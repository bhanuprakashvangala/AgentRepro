import qrcode
import cv2
import os
import argparse

OUTPUT_DIR = "qr_codes"

def generate_qr_code(data: str, filename: str):
    """Generates and saves a single QR code image."""
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)
        print(f"Successfully generated QR code: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating QR code for '{data}': {e}")
        return None

def read_qr_code(image_path: str):
    """Reads a QR code from an image file and returns the decoded data."""
    try:
        if not os.path.exists(image_path):
            print(f"Error: File not found at {image_path}")
            return None, image_path

        image = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        
        decoded_text, points, _ = detector.detectAndDecode(image)
        
        if points is not None:
            return decoded_text, image_path
        else:
            return None, image_path
    except Exception as e:
        print(f"An error occurred while reading {image_path}: {e}")
        return None, image_path

def run_demo():
    """Runs a self-contained demonstration of generating and reading QR codes."""
    print("--- Running Demo Mode ---")
    
    # 1. Generate QR codes
    print("\nStep 1: Generating sample QR codes...")
    demo_data = {
        "qr_hello.png": "Hello, World!",
        "qr_url.png": "https://www.google.com",
        "qr_data.png": "12345; some data; complete"
    }
    generated_files = []
    for filename, data in demo_data.items():
        path = generate_qr_code(data, filename)
        if path:
            generated_files.append(path)
    
    # 2. Read the generated QR codes (bulk operation)
    print("\nStep 2: Reading the generated QR codes...")
    if not generated_files:
        print("No files were generated, cannot run read step.")
        return

    for data, path in [read_qr_code(f) for f in generated_files]:
        if data:
            print(f"  - SUCCESS: Decoded '{path}' -> \"{data}\" ")
        else:
            print(f"  - FAILURE: Could not decode QR code in '{path}'.")
    print("\n--- Demo Complete ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and read QR codes.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Generate Command ---
    parser_gen = subparsers.add_parser("generate", help="Generate a QR code.")
    parser_gen.add_argument("-d", "--data", required=True, help="The data to encode in the QR code.")
    parser_gen.add_argument("-o", "--output", required=True, help="The output image filename (e.g., my_qr.png).")

    # --- Read Command ---
    parser_read = subparsers.add_parser("read", help="Read one or more QR code image files.")
    parser_read.add_argument("files", nargs='+', help="Path(s) to the QR code image files.")

    # --- Demo Command ---
    parser_demo = subparsers.add_parser("demo", help="Run a self-contained demo.")

    args = parser.parse_args()

    if args.command == "generate":
        generate_qr_code(args.data, args.output)
    elif args.command == "read":
        print(f"Reading {len(args.files)} file(s)...")
        for data, path in [read_qr_code(f) for f in args.files]:
            if data:
                print(f"  - SUCCESS: Decoded '{path}' -> \"{data}\" ")
            else:
                print(f"  - FAILURE: Could not decode QR code in '{path}'.")
    elif args.command == "demo":
        run_demo()
