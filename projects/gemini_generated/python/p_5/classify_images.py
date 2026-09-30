import os
import requests
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions

# --- Configuration ---
IMAGE_DIR = "sample_images"
IMAGE_URLS = {
    "cat.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat_paw.jpg/1024px-Cat_paw.jpg",
    "dog.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/German_Shepherd_-_DSC_0346_%2810096362833%29.jpg/1024px-German_Shepherd_-_DSC_0346_%2810096362833%29.jpg"
}

def download_sample_images():
    """Downloads sample images if they don't already exist."""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        print(f"Created directory: {IMAGE_DIR}")

    for filename, url in IMAGE_URLS.items():
        filepath = os.path.join(IMAGE_DIR, filename)
        if not os.path.exists(filepath):
            try:
                print(f"Downloading {filename}...")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {filename}: {e}")

def classify_image(image_path, model):
    """
    Loads, preprocesses, and classifies a single image, returning top predictions.
    """
    try:
        # Load and preprocess the image
        img = image.load_img(image_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Make prediction
        preds = model.predict(x)

        # Decode predictions to human-readable labels
        return decode_predictions(preds, top=3)[0]
    except Exception as e:
        print(f"Could not process file {image_path}: {e}")
        return None

if __name__ == "__main__":
    # 1. Ensure sample images are available
    download_sample_images()

    # 2. Load the pre-trained ResNet50 model
    print("\nLoading pre-trained ResNet50 model...")
    # This might take a moment on the first run as weights are downloaded.
    model = ResNet50(weights='imagenet')
    print("Model loaded successfully.")

    # 3. Classify all images in the directory
    print(f"\n--- Starting Image Classification in '{IMAGE_DIR}' ---")
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(IMAGE_DIR, filename)
            print(f"\nClassifying: {filename}")
            predictions = classify_image(filepath, model)
            
            if predictions:
                print("Predictions:")
                for imagenet_id, label, score in predictions:
                    print(f"  - {label}: {score:.2%}")
    print("\n--- Classification Complete ---")
