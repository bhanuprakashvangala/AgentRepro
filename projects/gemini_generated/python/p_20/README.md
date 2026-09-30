# File Deduplication Tool

This is a command-line tool to find and safely handle duplicate files within a directory and its subdirectories.

## ⚠️ Important: Safety First

This script **moves** files it identifies as duplicates. It does **not** delete them permanently. Duplicates are moved to a timestamped `duplicates_backup_...` directory, giving you a chance to review them. However, you should always be cautious when running file system utilities. **It is recommended to back up important data before use.**

## Features

- **Content-Based Detection**: Files are identified as duplicates by comparing their SHA256 hash, not by their name, date, or location.
- **Efficient Scanning**: Uses a two-pass approach, first filtering by file size and then hashing, which is much faster than hashing every single file.
- **Recursive**: Scans all subdirectories within the given path.
- **Safe Removal**: Moves duplicates to a backup folder instead of deleting them.
- **Self-Contained Demo**: Includes a `setup-demo` command to create a safe environment for you to test the tool's functionality.

## Usage

This tool uses only standard Python libraries, so no external packages are needed.

### 1. (Recommended) Run the Demo

This is the best way to see how the tool works in a safe environment.

**First, create the demo directory:**
```bash
python deduplicator.py setup-demo
```
This will create a folder named `demo_duplicates/` containing a few text files, some of which are identical.

**Next, scan the demo directory:**
```bash
python deduplicator.py scan demo_duplicates
```

The script will scan the folder, report its findings, and move the identified duplicates into a new `duplicates_backup_...` folder.

### 2. Scan Your Own Directory

Once you are comfortable with how the tool works, you can run it on one of your own directories.

```bash
python deduplicator.py scan "/path/to/your/folder"
```
*(Remember to use quotes if your path contains spaces)*
