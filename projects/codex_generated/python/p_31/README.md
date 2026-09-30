# Multi-format Compression Tool

Compress files and directories into `.zip`, `.tar.gz`, or `.tar.bz2` archives with optional compression level and progress display.

## Setup
(Optional virtual environment)
```bash
python3 -m venv .venv
source .venv/bin/activate
```
No external dependencies are required; the script uses Python's standard library.

## Usage
```bash
python compress.py --input src/ docs/ --output backup.tar.gz --compression-level 6
```

Options:
- `--input`: One or more files/directories (recursively added).
- `--output`: Destination archive (`.zip`, `.tar.gz`, `.tar.bz2`).
- `--compression-level`: Integer 0-9 (zip, gzip, bzip2). `0` stores without compression when supported.
- `--overwrite`: Overwrite existing archive if it exists.

Progress is shown on stderr. The script writes the final archive to the specified path.
