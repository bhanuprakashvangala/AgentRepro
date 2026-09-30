# File Encryption/Decryption Tool

This Python script provides AES encryption and decryption for files of any type with secure key management and progress indicators.

## Requirements

- Python 3.7+

## Installation

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Encrypt a file

```bash
python file_encryptor.py encrypt <input_file> <output_file>
```

This will generate a key file named `encryption.key` in the current directory.

### Decrypt a file

```bash
python file_encryptor.py decrypt <encrypted_file> <output_file>
```

Make sure the `encryption.key` file is in the current directory.

### Example

```bash
# Encrypt
python file_encryptor.py encrypt document.pdf document.pdf.enc

# Decrypt
python file_encryptor.py decrypt document.pdf.enc decrypted_document.pdf
```

## Security Notes

- Keep your `encryption.key` file secure and never share it
- The key file is required for decryption
- Losing the key means losing access to encrypted files
