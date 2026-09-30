# Face Detection with OpenCV

This is a command-line tool that detects human faces in images using a pre-trained Haar Cascade model from OpenCV.

## Features

- **Automatic Setup**: The script automatically downloads the necessary assets on its first run:
    - The `haarcascade_frontalface_default.xml` model file.
    - A sample image (`sample_presidents.jpg`) for the demo mode.
- **Face Detection**: Uses OpenCV's highly reliable Haar Cascade classifier.
- **Bounding Boxes**: Draws green rectangles around all detected faces.
- **Batch Processing**: Can process multiple image files in a single command.
- **Organized Output**: Saves the processed images into an `output_images/` directory.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Recommended) Run the Demo:**
    This is the easiest way to see the tool work. It will download the required model and a sample image, then process it.
    ```bash
    python face_detector.py --demo
    ```

4.  **Process Your Own Images:**
    Provide the path to one or more image files.
    ```bash
    # Process a single image
    python face_detector.py my_photo.jpg

    # Process multiple images at once
    python face_detector.py image1.png image2.jpg
    ```

## Output

For each image processed, a new file named `detected_<original_filename>` will be saved in the `output_images/` directory. This new image will have green bounding boxes drawn around any detected faces.
