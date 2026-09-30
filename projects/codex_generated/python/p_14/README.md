# AES File Encryption Tool

Command-line utility for encrypting and decrypting files with AES-GCM. Includes password-based key derivation, optional key files, and progress indicators for large inputs.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Generate a key file (optional)

```bash
python secure_file.py generate-key --key-file secret.key
```

This creates a base64-encoded 32-byte key suitable for repeated use. Keep the key file private.

## Encrypt a file

### Using a password (PBKDF2 with per-file salt)
```bash
python secure_file.py encrypt --input report.pdf --output report.pdf.enc --password "StrongPassphrase"
```

### Using a key file
```bash
python secure_file.py encrypt --input archive.tar --output archive.tar.enc --key-file secret.key
```

## Decrypt a file

```bash
python secure_file.py decrypt --input report.pdf.enc --output report.pdf --password "StrongPassphrase"
# or
python secure_file.py decrypt --input archive.tar.enc --output archive.tar --key-file secret.key
```

During processing the script prints a percentage progress indicator to stderr. Encrypted files include metadata (version, salt, nonce) to allow safe decryption.

> **Security notes**
> - Password-derived keys use PBKDF2-HMAC-SHA256 with 200k iterations and a random salt per file.
> - AES-256-GCM ensures confidentiality and integrity; tampering raises a decryption error.
> - Store generated key files securely (permissions are set to `0600` on POSIX systems).
