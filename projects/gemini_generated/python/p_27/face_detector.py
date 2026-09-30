import cv2
import os
import argparse
import requests

# --- Configuration ---
# URL for the pre-trained Haar Cascade model file
CASCADE_URL = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
CASCADE_FILENAME = "haarcascade_frontalface_default.xml"

# URL for a sample image for the demo
DEMO_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Presidents_of_the_United_States.jpg/1920px-Presidents_of_the_United_States.jpg"
DEMO_IMAGE_FILENAME = "sample_presidents.jpg"

OUTPUT_DIR = "output_images"

# --- Helper Functions ---
def download_file(url, filename, description):
    """Downloads a file if it doesn't already exist."""
    if os.path.exists(filename):
        print(f"[INFO] {description} file already exists: '{filename}'")
        return
    
    print(f"[INFO] Downloading {description}: {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[INFO] Download complete.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not download {filename}: {e}")
        exit()

def detect_and_draw(image_path, cascade_path, output_dir):
    """Detects faces in an image, draws bounding boxes, and saves the result."""
    print(f"\nProcessing image: {image_path}")
    try:
        # Load the classifier and the image
        face_cascade = cv2.CascadeClassifier(cascade_path)
        image = cv2.imread(image_path)
        if image is None:
            print(f"[ERROR] Could not read image file: {image_path}")
            return

        # Convert image to grayscale for the detector
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        # scaleFactor, minNeighbors, and minSize can be tuned for performance/accuracy
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        print(f"Found {len(faces)} face(s) in the image.")

        # Draw a rectangle around each detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Save the resulting image
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_filename = os.path.join(output_dir, "detected_" + os.path.basename(image_path))
        cv2.imwrite(output_filename, image)
        print(f"Saved result to: {output_filename}")

    except Exception as e:
        print(f"[ERROR] An error occurred processing {image_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect faces in images using OpenCV.")
    parser.add_argument("files", nargs='*', help="Path(s) to image files to process.")
    parser.add_argument("--demo", action="store_true", help="Run a demo with a sample image.")
    args = parser.parse_args()

    # --- Asset Management ---
    # Ensure the necessary Haar Cascade file is present before starting
    download_file(CASCADE_URL, CASCADE_FILENAME, "Haar Cascade model")

    if args.demo:
        download_file(DEMO_IMAGE_URL, DEMO_IMAGE_FILENAME, "sample demo image")
        files_to_process = [DEMO_IMAGE_FILENAME]
    elif args.files:
        files_to_process = args.files
    else:
        parser.print_help()
        exit()

    # --- Main Processing Loop ---
    if files_to_process:
        for file_path in files_to_process:
            if not os.path.exists(file_path):
                print(f"[ERROR] Input file not found: '{file_path}'. Skipping.")
                continue
            detect_and_draw(file_path, CASCADE_FILENAME, OUTPUT_DIR)
    
    print("\n--- Process Complete ---")
