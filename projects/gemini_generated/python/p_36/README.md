# Image Resize and Optimization Tool

This is a command-line tool to batch resize and optimize images using the `Pillow` library.

## Features

- **Batch Processing**: Process multiple images at once by providing multiple file paths or entire directories as input.
- **Aspect Ratio Preservation**: Intelligently resizes images to a target width or height while maintaining the original aspect ratio.
- **Image Optimization**: Reduces file size by applying optimization. For JPEG files, you can control the output quality.
- **Reproducible Demo**: Includes a `--demo` mode that automatically downloads sample images to a `source_images/` directory and processes them, providing a quick and easy end-to-end test.

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
    This is the best way to see the tool in action. It will download sample images and resize them to a width of 500 pixels.
    ```bash
    python image_tool.py --demo --width 500
    ```
    Check the `processed_images/` folder for the results.

4.  **Process Your Own Images:**
    Provide the path to your files or directories. You must specify at least a `--width` or a `--height`.

    **Resize a single image to a width of 800px:**
    ```bash
    python image_tool.py my_image.jpg --width 800
    ```

    **Resize all images in a directory to a height of 1080px:**
    ```bash
    python image_tool.py /path/to/my/images/ --height 1080
    ```

    **Resize and set JPEG quality:**
    ```bash
    python image_tool.py my_photo.jpeg --width 1920 --quality 75
    ```

    **Fit images within a bounding box (e.g., 600x600):**
    The tool will resize the image so it fits inside the box while maintaining its aspect ratio.
    ```bash
    python image_tool.py my_image.png --width 600 --height 600
    ```

## Output

All processed images will be saved in the specified output directory (default is `processed_images/`).
