# Image Classifier with TensorFlow

This script uses a pre-trained ResNet50 model from TensorFlow/Keras to classify images from a local folder. It automatically downloads sample images for a quick and easy demonstration.

## Features

- Loads the powerful, pre-trained ResNet50 model.
- Automatically downloads sample images (`cat.jpg`, `dog.jpg`) on the first run.
- Processes all images in the `sample_images` directory.
- Outputs the top 3 predictions with confidence scores for each image.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    *Note: TensorFlow is a large library and may take some time to install.*
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```bash
    python classify_images.py
    ```

## Expected Output

When you run the script for the first time, it will download the sample images and the ResNet50 model weights. Then, it will output the classification results to your console, for instance:

```
--- Starting Image Classification in 'sample_images' ---

Classifying: cat.jpg
Predictions:
  - tabby: 53.27%
  - Egyptian_cat: 29.28%
  - tiger_cat: 10.93%

Classifying: dog.jpg
Predictions:
  - German_shepherd: 97.21%
  - malinois: 1.29%
  - Appenzeller: 0.23%

--- Classification Complete ---
```
*(Actual percentages may vary slightly)*
