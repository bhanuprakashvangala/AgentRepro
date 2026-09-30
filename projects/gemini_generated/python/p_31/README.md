# File Compression Tool

This is a command-line tool for compressing files and directories into various archive formats using Python's standard library.

## Features

- **Multiple Formats**: Supports creating `.zip`, `.tar.gz`, and `.tar.bz2` archives.
- **No Dependencies**: Built entirely with Python's standard libraries, so no external packages are needed.
- **Recursive Addition**: Automatically includes all files and subdirectories when you provide a directory as input.
- **Compression Level**: Allows specifying a compression level (1-9) for the `.zip` format.
- **Progress Indicator**: Displays progress by showing which file is currently being added to the archive.
- **Reproducible Demo**: Includes a `setup-demo` command to create a sample folder structure, making it easy to test the tool.

## Usage

No installation is required beyond having a standard Python interpreter.

### 1. (Recommended) Set up the Demo Directory

This command creates a folder named `demo_files_to_compress/` with some sample files inside. This is the best way to test the compression commands safely.

```bash
python compress_tool.py setup-demo
```

### 2. Compress Files

Use the `compress` command with the desired inputs, output file, and format.

**Example 1: Create a ZIP archive**

This command compresses the entire demo directory into a zip file with the highest compression level.
```bash
python compress_tool.py compress demo_files_to_compress/ -o my_archive.zip -f zip --level 9
```

**Example 2: Create a TAR.GZ archive**

This command compresses the demo directory into a `.tar.gz` file.
```bash
python compress_tool.py compress demo_files_to_compress/ -o my_archive.tar.gz -f tar.gz
```

**Example 3: Create a TAR.BZ2 archive**

This command compresses the demo directory into a `.tar.bz2` file.
```bash
python compress_tool.py compress demo_files_to_compress/ -o my_archive.tar.bz2 -f tar.bz2
```

**Example 4: Compress specific files**

You can also specify individual files as input.
```bash
python compress_tool.py compress demo_files_to_compress/file1.txt demo_files_to_compress/file2.log -o specific_files.zip -f zip
```
