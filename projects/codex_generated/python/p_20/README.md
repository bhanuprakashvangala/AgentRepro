# File Deduplication Tool

Scans directories for duplicate files using content hashes and optionally deletes or moves duplicates to a backup folder.

## Setup

Only the Python standard library is required. For isolation you can still create a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Usage

```bash
python deduplicate.py --paths /path/to/dir1 /path/to/dir2 --hash sha256 --min-size 1024
```

Flags:
- `--paths`: One or more directories to scan (recursive).
- `--hash`: Hash algorithm (`sha256` default, or `md5`).
- `--min-size`: Skip files smaller than this many bytes (default `1`).
- `--delete`: Remove duplicates (keeping the first file found). Use with caution.
- `--backup-dir`: When combined with `--delete`, move duplicates into this directory instead of unlinking them.
- `--dry-run`: Show planned actions without modifying files.

### Examples

List duplicates without deleting:
```bash
python deduplicate.py --paths ./photos ./videos
```

Delete duplicates, moving copies into `./duplicates_backup`:
```bash
python deduplicate.py \
  --paths ./media \
  --delete \
  --backup-dir ./duplicates_backup
```

All deletions/moves apply only to files beyond the first copy encountered per hash. Use `--dry-run` before destructive operations to verify behaviour.
