import os
import argparse
import zipfile
import tarfile
from contextlib import closing

def setup_demo_directory(demo_path="demo_files_to_compress"):
    """Creates a sample directory with files for demonstration."""
    print(f"--- Setting up demo directory at '{demo_path}' ---")
    if os.path.exists(demo_path):
        print("Demo directory already exists.")
        return

    os.makedirs(demo_path)
    sub_path = os.path.join(demo_path, "subdirectory")
    os.makedirs(sub_path)

    with open(os.path.join(demo_path, "file1.txt"), 'w') as f:
        f.write("This is the first sample file.\n" * 100)
    with open(os.path.join(demo_path, "file2.log"), 'w') as f:
        f.write("This is the second sample file, a log.\n" * 50)
    with open(os.path.join(sub_path, "file3.dat"), 'w') as f:
        f.write("This is a file in a subdirectory.\n" * 200)
    print("Demo directory created successfully.")

def _get_files_to_archive(sources):
    """Recursively collects all file paths from the source paths."""
    file_paths = []
    for source in sources:
        if os.path.isdir(source):
            for dirpath, _, filenames in os.walk(source):
                for filename in filenames:
                    file_paths.append(os.path.join(dirpath, filename))
        elif os.path.isfile(source):
            file_paths.append(source)
    return file_paths

def create_zip_archive(output_filename, sources, compress_level):
    """Creates a .zip archive from a list of source files/directories."""
    print(f"Creating ZIP archive: {output_filename}")
    files_to_add = _get_files_to_archive(sources)
    total_files = len(files_to_add)

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=compress_level) as zipf:
        for i, file_path in enumerate(files_to_add):
            # arcname makes paths relative inside the zip
            arcname = os.path.relpath(file_path, start=os.path.dirname(sources[0]))
            zipf.write(file_path, arcname)
            print(f"  -> Adding file {i+1}/{total_files}: {file_path}")
    print("ZIP archive created successfully.")

def create_tar_archive(output_filename, sources, mode):
    """Creates a .tar.gz or .tar.bz2 archive."""
    print(f"Creating TAR archive: {output_filename}")
    files_to_add = _get_files_to_archive(sources)
    total_files = len(files_to_add)

    with tarfile.open(output_filename, mode) as tarf:
        for i, file_path in enumerate(files_to_add):
            arcname = os.path.relpath(file_path, start=os.path.dirname(sources[0]))
            tarf.add(file_path, arcname=arcname)
            print(f"  -> Adding file {i+1}/{total_files}: {file_path}")
    print("TAR archive created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compress files and directories into an archive.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Setup Demo Command ---
    parser_demo = subparsers.add_parser("setup-demo", help="Create a sample directory to compress.")

    # --- Compress Command ---
    parser_comp = subparsers.add_parser("compress", help="Compress files/directories.")
    parser_comp.add_argument("inputs", nargs='+', help="One or more source files or directories to compress.")
    parser_comp.add_argument("-o", "--output", required=True, help="Path for the output archive file.")
    parser_comp.add_argument("-f", "--format", choices=['zip', 'tar.gz', 'tar.bz2'], required=True, help="The archive format.")
    parser_comp.add_argument("-l", "--level", type=int, default=9, choices=range(1, 10), help="Compression level (1-9) for ZIP format only.")

    args = parser.parse_args()

    if args.command == "setup-demo":
        setup_demo_directory()
    elif args.command == "compress":
        if args.format == 'zip':
            create_zip_archive(args.output, args.inputs, args.level)
        elif args.format == 'tar.gz':
            create_tar_archive(args.output, args.inputs, mode='w:gz')
        elif args.format == 'tar.bz2':
            create_tar_archive(args.output, args.inputs, mode='w:bz2')
