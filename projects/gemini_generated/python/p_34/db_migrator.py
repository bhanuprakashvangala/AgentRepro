import os
import sqlite3
import argparse
import re

# --- Configuration ---
DB_FILE = "app.db"
MIGRATIONS_DIR = "migrations"

# --- Helper Functions ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def setup_project():
    """Creates the migrations directory and the migration files for the demo."""
    if not os.path.exists(MIGRATIONS_DIR):
        print(f"Creating directory: {MIGRATIONS_DIR}")
        os.makedirs(MIGRATIONS_DIR)

    migrations = {
        "001_create_users_table.sql": "-- UP\nCREATE TABLE users (\n    id INTEGER PRIMARY KEY,\n    name TEXT NOT NULL,\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n-- DOWN\nDROP TABLE users;",
        "002_create_products_table.sql": "-- UP\nCREATE TABLE products (\n    id INTEGER PRIMARY KEY,\n    product_name TEXT NOT NULL,\n    price INTEGER\n);\n-- DOWN\nDROP TABLE products;"
    }

    for filename, content in migrations.items():
        path = os.path.join(MIGRATIONS_DIR, filename)
        if not os.path.exists(path):
            print(f"Creating migration file: {path}")
            with open(path, 'w') as f:
                f.write(content)

def get_current_version(conn):
    """Gets the current schema version from the database."""
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);")
        cursor.execute("SELECT version FROM schema_version;")
        result = cursor.fetchone()
        if result is None:
            cursor.execute("INSERT INTO schema_version (version) VALUES (0);")
            conn.commit()
            return 0
        return result[0]
    except sqlite3.Error as e:
        print(f"[ERROR] Database error: {e}")
        return -1

def get_migration_files():
    """Returns a sorted list of migration files from the migrations directory."""
    try:
        files = [f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')]
        return sorted(files, key=lambda x: int(x.split('_')[0]))
    except FileNotFoundError:
        print(f"[ERROR] Migrations directory '{MIGRATIONS_DIR}' not found.")
        return []

# --- Core Logic ---
def migrate():
    """Applies all available migrations that have not yet been run."""
    conn = get_db_connection()
    current_version = get_current_version(conn)
    migration_files = get_migration_files()
    
    applied_count = 0
    for migration_file in migration_files:
        version = int(migration_file.split('_')[0])
        if version > current_version:
            print(f"Applying migration {migration_file}...")
            with open(os.path.join(MIGRATIONS_DIR, migration_file), 'r') as f:
                # Extract the -- UP section
                sql = f.read().split("-- DOWN")[0].replace("-- UP", "").strip()
            
            try:
                conn.execute(sql)
                conn.execute("UPDATE schema_version SET version = ?", (version,))
                conn.commit()
                print("  -> Success.")
                applied_count += 1
            except sqlite3.Error as e:
                print(f"[ERROR] Failed to apply migration {migration_file}: {e}")
                conn.rollback()
                break
    conn.close()
    if applied_count == 0:
        print("Database is already up to date.")

def rollback():
    """Rolls back the most recent migration."""
    conn = get_db_connection()
    current_version = get_current_version(conn)

    if current_version == 0:
        print("Database is at version 0. Nothing to roll back.")
        return

    migration_file_to_revert = None
    for f in get_migration_files():
        if f.startswith(f"{current_version:03d}"):
            migration_file_to_revert = f
            break

    if not migration_file_to_revert:
        print(f"[ERROR] Could not find migration file for version {current_version}.")
        return

    print(f"Rolling back migration {migration_file_to_revert}...")
    with open(os.path.join(MIGRATIONS_DIR, migration_file_to_revert), 'r') as f:
        # Extract the -- DOWN section
        sql = f.read().split("-- DOWN")[1].strip()

    try:
        conn.execute(sql)
        previous_version = current_version - 1
        conn.execute("UPDATE schema_version SET version = ?", (previous_version,))
        conn.commit()
        print("  -> Success.")
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to roll back migration: {e}")
        conn.rollback()
    conn.close()

def status():
    """Shows the current database version and available migrations."""
    conn = get_db_connection()
    current_version = get_current_version(conn)
    conn.close()
    print(f"Current DB Version: {current_version}")
    print("\nAvailable Migrations:")
    for f in get_migration_files():
        version = int(f.split('_')[0])
        applied_status = "(applied)" if version <= current_version else "(pending)"
        print(f"  - {f} {applied_status}")

if __name__ == "__main__":
    setup_project()
    parser = argparse.ArgumentParser(description="A simple database migration tool.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    subparsers.add_parser("migrate", help="Apply all pending migrations.")
    subparsers.add_parser("rollback", help="Roll back the last applied migration.")
    subparsers.add_parser("status", help="Show the current migration status.")

    args = parser.parse_args()

    if args.command == "migrate":
        migrate()
    elif args.command == "rollback":
        rollback()
    elif args.command == "status":
        status()
