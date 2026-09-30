# QR Code Generator and Reader

This is a command-line tool for generating and reading QR codes from image files using Python.

## Features

- **Generate QR Codes**: Create QR code images from any string data.
- **Read QR Codes**: Decode QR codes from existing image files.
- **Bulk Operations**: Read multiple QR code files in a single command.
- **Demo Mode**: A self-contained demonstration that generates and then reads QR codes to verify functionality.
- **Organized Output**: Generated QR codes are saved into a `qr_codes/` directory.

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

### Recommended: Run the Demo

This is the easiest way to see the tool work. It will create a `qr_codes/` directory, generate three sample QR codes inside it, and then immediately try to read them.

```bash
python qr_tool.py demo
```

### Generate a QR Code

Use the `generate` command with the data you want to encode and an output filename.

```bash
python qr_tool.py generate --data "https://www.example.com" --output "website.png"
```
This will create the file `qr_codes/website.png`.

### Read QR Code(s)

Use the `read` command followed by the path(s) to one or more image files.

**Read a single file:**
```bash
python qr_tool.py read qr_codes/website.png
```

**Read multiple files (bulk operation):**
```bash
# First, create a few files to read
python qr_tool.py generate --data "First file" --output "file1.png"
python qr_tool.py generate --data "Second file" --output "file2.png"

# Now, read them both
python qr_tool.py read qr_codes/file1.png qr_codes/file2.png
```
