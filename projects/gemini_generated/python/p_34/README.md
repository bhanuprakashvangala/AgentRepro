# Custom Database Migration Tool

This project is a lightweight, command-line database migration tool built from scratch in Python. It demonstrates the fundamental principles of schema versioning without relying on large frameworks like Alembic.

## Features

- **Pure Python**: Uses only the standard library (`sqlite3`, `os`, `argparse`), requiring no external dependencies.
- **File-Based Migrations**: Reads schema changes from simple `.sql` files stored in a `migrations/` directory.
- **Schema Versioning**: Tracks the current database version in a dedicated `schema_version` table within the database itself.
- **Apply & Rollback**: Supports applying pending migrations (`migrate`) and reverting the most recent one (`rollback`).
- **Status Check**: A `status` command shows the current database version and the status of all available migration files.
- **Self-Contained**: Automatically creates the database file (`app.db`) and migration scripts on first run.

## How It Works

The tool reads SQL files from the `migrations/` directory. Each file is named with a version number (e.g., `001_...`, `002_...`) and must contain `-- UP` and `-- DOWN` sections, which define the SQL commands for applying and reverting the migration, respectively.

## Usage

No installation is required beyond having a standard Python interpreter. The script will automatically create the necessary `migrations/` directory and SQL files when you run it.

### 1. Check Initial Status

See the current state of the database before making changes.
```bash
python db_migrator.py status
```
*Expected Output: Shows current version is 0 and both migrations are pending.*

### 2. Apply Migrations

Apply all pending migrations to bring the database to the latest version.
```bash
python db_migrator.py migrate
```
*Expected Output: Shows migrations 001 and 002 being applied successfully.*

### 3. Check Status Again

Verify that the database is now at the latest version.
```bash
python db_migrator.py status
```
*Expected Output: Shows current version is 2 and both migrations are applied.*

### 4. Roll Back a Migration

Revert the most recently applied migration.
```bash
python db_migrator.py rollback
```
*Expected Output: Shows migration 002 being rolled back.*

### 5. Check Final Status

Confirm that the database has been rolled back to the previous version.
```bash
python db_migrator.py status
```
*Expected Output: Shows current version is 1. Migration 001 is applied, and 002 is pending.*
