#!/usr/bin/env python3
"""Simple database migration tool with version tracking and rollback support."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
DEFAULT_DATABASE = Path(__file__).resolve().parent / "database.db"


@dataclass
class Migration:
    version: str
    name: str
    module_path: Path
    upgrade: Callable[[sqlite3.Connection], None]
    downgrade: Callable[[sqlite3.Connection], None]


class MigrationError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DATABASE),
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current migration status")
    subparsers.add_parser("history", help="Show migration history")

    upgrade_parser = subparsers.add_parser("upgrade", help="Apply pending migrations")
    upgrade_parser.add_argument(
        "--target",
        help="Target version to upgrade to (default: latest)",
    )

    downgrade_parser = subparsers.add_parser("downgrade", help="Rollback migrations")
    group = downgrade_parser.add_mutually_exclusive_group()
    group.add_argument("--steps", type=int, help="Number of migrations to rollback")
    group.add_argument("--target", help="Target version to rollback to")

    return parser.parse_args()


def load_migrations() -> List[Migration]:
    if not MIGRATIONS_DIR.exists():
        raise MigrationError(f"Migrations directory not found: {MIGRATIONS_DIR}")

    migrations: List[Migration] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        stem = path.stem
        if "_" not in stem:
            raise MigrationError(f"Migration filename must start with version_ prefix: {path.name}")
        version, name = stem.split("_", 1)
        module = import_module_from_path(path)
        if not hasattr(module, "upgrade") or not hasattr(module, "downgrade"):
            raise MigrationError(f"Migration {path.name} must define upgrade(conn) and downgrade(conn)")
        migrations.append(
            Migration(
                version=version,
                name=name,
                module_path=path,
                upgrade=getattr(module, "upgrade"),
                downgrade=getattr(module, "downgrade"),
            )
        )
    return migrations


def import_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise MigrationError(f"Unable to import migration module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_schema_table(conn)
    return conn


def ensure_schema_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def fetch_applied_versions(conn: sqlite3.Connection) -> Dict[str, str]:
    cursor = conn.execute("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at")
    return {row["version"]: row["applied_at"] for row in cursor.fetchall()}


def current_version(applied: Dict[str, str]) -> Optional[str]:
    if not applied:
        return None
    return list(applied.keys())[-1]


def status(conn: sqlite3.Connection, migrations: List[Migration]) -> None:
    applied = fetch_applied_versions(conn)
    current = current_version(applied)
    print(f"Database: {conn.execute('PRAGMA database_list').fetchone()['file']}")
    print(f"Current version: {current or 'None'}")
    pending = [m for m in migrations if m.version not in applied]
    print(f"Applied migrations: {len(applied)}")
    print(f"Pending migrations: {len(pending)}")
    if pending:
        print("Pending versions:")
        for migration in pending:
            print(f"  {migration.version} - {migration.name}")


def history(conn: sqlite3.Connection, migrations: List[Migration]) -> None:
    applied = fetch_applied_versions(conn)
    print("Migration history:")
    for migration in migrations:
        mark = "[x]" if migration.version in applied else "[ ]"
        applied_at = applied.get(migration.version, "-")
        print(f"{mark} {migration.version} {migration.name} applied_at={applied_at}")


def upgrade(conn: sqlite3.Connection, migrations: List[Migration], target: Optional[str]) -> None:
    applied = fetch_applied_versions(conn)
    pending = [m for m in migrations if m.version not in applied]
    if not pending:
        print("No migrations to apply.")
        return

    if target:
        pending_versions = [m.version for m in pending]
        if target not in pending_versions:
            raise MigrationError(f"Target version {target} is not pending.")
        pending = [m for m in pending if m.version <= target]

    for migration in pending:
        print(f"Applying {migration.version} - {migration.name}...")
        apply_migration(conn, migration, direction="upgrade")
    print("Upgrade complete.")


def downgrade(
    conn: sqlite3.Connection,
    migrations: List[Migration],
    *,
    steps: Optional[int],
    target: Optional[str],
) -> None:
    applied = fetch_applied_versions(conn)
    if not applied:
        print("No migrations have been applied.")
        return

    applied_versions = [m for m in migrations if m.version in applied]
    if not applied_versions:
        print("No migrations have been applied.")
        return

    applied_versions.sort(key=lambda m: m.version, reverse=True)

    if steps is not None:
        if steps <= 0:
            raise MigrationError("Steps must be positive")
        to_rollback = applied_versions[:steps]
    elif target:
        to_rollback = []
        for migration in applied_versions:
            to_rollback.append(migration)
            if migration.version == target:
                break
        else:
            raise MigrationError(f"Target version {target} not found in applied migrations")
    else:
        # default to single step
        to_rollback = applied_versions[:1]

    for migration in to_rollback:
        print(f"Reverting {migration.version} - {migration.name}...")
        apply_migration(conn, migration, direction="downgrade")
    print("Downgrade complete.")


def apply_migration(conn: sqlite3.Connection, migration: Migration, *, direction: str) -> None:
    if direction not in {"upgrade", "downgrade"}:
        raise ValueError("direction must be 'upgrade' or 'downgrade'")

    func = migration.upgrade if direction == "upgrade" else migration.downgrade
    try:
        with conn:
            func(conn)
            if direction == "upgrade":
                conn.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (migration.version, dt.datetime.utcnow().isoformat() + "Z"),
                )
            else:
                conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,),
                )
    except Exception as exc:
        raise MigrationError(
            f"Failed to {direction} migration {migration.version}: {exc}"
        ) from exc


def main() -> None:
    args = parse_args()
    migrations = load_migrations()
    conn = get_connection(args.database)

    if args.command == "status":
        status(conn, migrations)
    elif args.command == "history":
        history(conn, migrations)
    elif args.command == "upgrade":
        upgrade(conn, migrations, args.target)
    elif args.command == "downgrade":
        downgrade(conn, migrations, steps=args.steps, target=args.target)


if __name__ == "__main__":
    try:
        main()
    except MigrationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
*** End Patch
