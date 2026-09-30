import os
import hashlib
import argparse
import shutil
from collections import defaultdict
from datetime import datetime

CHUNK_SIZE = 65536  # 64kb

def get_file_hash(file_path):
    """Calculates the SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except IOError:
        return None

def find_duplicates(scan_path):
    """Finds duplicate files in a given path using a two-pass method."""
    print(f"Scanning directory: {scan_path}\n")
    files_by_size = defaultdict(list)
    files_by_hash = defaultdict(list)
    duplicates = {}

    # Pass 1: Group files by size
    for dirpath, _, filenames in os.walk(scan_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 0: # Ignore empty files
                    files_by_size[file_size].append(file_path)
            except OSError:
                continue # Skip broken links or inaccessible files

    # Pass 2: Hash files for groups with identical sizes
    for size in files_by_size:
        if len(files_by_size[size]) > 1:
            for file_path in files_by_size[size]:
                file_hash = get_file_hash(file_path)
                if file_hash:
                    files_by_hash[file_hash].append(file_path)

    # Filter for hashes with more than one file path (actual duplicates)
    for file_hash in files_by_hash:
        if len(files_by_hash[file_hash]) > 1:
            duplicates[file_hash] = files_by_hash[file_hash]

    return duplicates

def process_duplicates(duplicate_map, backup_dir):
    """Moves duplicate files to a backup directory, keeping one original."""
    if not duplicate_map:
        print("No duplicate files found.")
        return

    print(f"\nFound {len(duplicate_map)} set(s) of duplicate files.")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")

    total_moved = 0
    for file_list in duplicate_map.values():
        # Keep the first file, move the rest
        original = file_list[0]
        copies = file_list[1:]
        print(f"  - Keeping: {original}")
        for copy_path in copies:
            try:
                shutil.move(copy_path, backup_dir)
                print(f"    - Moved:   {copy_path}")
                total_moved += 1
            except shutil.Error as e:
                print(f"    - ERROR moving {copy_path}: {e}")
    
    print(f"\nProcess complete. Moved {total_moved} duplicate file(s) to {backup_dir}")

def setup_demo_directory(demo_path="demo_duplicates"):
    """Creates a sample directory with duplicate files for testing."""
    print(f"--- Setting up demo directory at '{demo_path}' ---")
    if os.path.exists(demo_path):
        shutil.rmtree(demo_path)
    
    sub_path1 = os.path.join(demo_path, "subfolder1")
    sub_path2 = os.path.join(demo_path, "subfolder2")
    os.makedirs(sub_path1)
    os.makedirs(sub_path2)

    # Create files
    with open(os.path.join(demo_path, "original_A.txt"), 'w') as f: f.write("This is file A.")
    with open(os.path.join(sub_path1, "copy_of_A.txt"), 'w') as f: f.write("This is file A.")
    with open(os.path.join(sub_path2, "another_copy_of_A.txt"), 'w') as f: f.write("This is file A.")
    with open(os.path.join(sub_path1, "unique_B.txt"), 'w') as f: f.write("This is file B.")
    with open(os.path.join(sub_path2, "unique_C.txt"), 'w') as f: f.write("This is file C.")
    print("Demo directory created successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and safely remove duplicate files.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Setup Demo Command ---
    parser_demo = subparsers.add_parser("setup-demo", help="Create a sample directory with duplicates to test the tool.")

    # --- Scan Command ---
    parser_scan = subparsers.add_parser("scan", help="Scan a directory for duplicate files.")
    parser_scan.add_argument("path", help="The directory to scan recursively.")

    args = parser.parse_args()

    if args.command == "setup-demo":
        setup_demo_directory()
    elif args.command == "scan":
        if not os.path.isdir(args.path):
            print(f"Error: Path '{args.path}' is not a valid directory.")
        else:
            duplicates_found = find_duplicates(args.path)
            backup_directory = "duplicates_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            process_duplicates(duplicates_found, backup_directory)
