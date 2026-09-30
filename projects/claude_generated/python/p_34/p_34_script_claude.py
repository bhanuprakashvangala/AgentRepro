#!/usr/bin/env python3
"""
Database Migration Tool with Alembic Integration and Custom Migration Support
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import click
from colorama import init, Fore, Style
from sqlalchemy import (
    create_engine, text, Column, Integer, String,
    DateTime, MetaData, Table, inspect
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base
from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext

# Initialize colorama for cross-platform colored output
init(autoreset=True)

Base = declarative_base()


class MigrationHistory(Base):
    """Track applied migrations in the database"""
    __tablename__ = 'migration_history'

    id = Column(Integer, primary_key=True)
    version = Column(String(255), unique=True, nullable=False)
    description = Column(String(500))
    applied_at = Column(DateTime, default=datetime.utcnow)
    checksum = Column(String(64))
    migration_type = Column(String(50), default='alembic')  # 'alembic' or 'custom'


class DatabaseMigrationTool:
    """Main migration tool class"""

    def __init__(self, db_url: str, migrations_dir: str = "migrations"):
        self.db_url = db_url
        self.migrations_dir = Path(migrations_dir)
        self.custom_migrations_dir = self.migrations_dir / "custom"
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def initialize(self) -> bool:
        """Initialize migration tracking table and Alembic"""
        try:
            # Create migration history table
            Base.metadata.create_all(self.engine)
            click.echo(f"{Fore.GREEN}✓ Migration history table created/verified")

            # Initialize Alembic if not already done
            if not (self.migrations_dir / "alembic.ini").exists():
                self._init_alembic()
            else:
                click.echo(f"{Fore.YELLOW}! Alembic already initialized")

            # Create custom migrations directory
            self.custom_migrations_dir.mkdir(parents=True, exist_ok=True)
            click.echo(f"{Fore.GREEN}✓ Custom migrations directory ready")

            return True
        except Exception as e:
            click.echo(f"{Fore.RED}✗ Initialization failed: {e}")
            return False

    def _init_alembic(self):
        """Initialize Alembic configuration"""
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Create alembic.ini
        alembic_ini = self.migrations_dir / "alembic.ini"
        alembic_ini_content = f"""[alembic]
script_location = {self.migrations_dir}/alembic
sqlalchemy.url = {self.db_url}
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
truncate_slug_length = 40

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        alembic_ini.write_text(alembic_ini_content)

        # Initialize Alembic
        alembic_cfg = Config(str(alembic_ini))
        command.init(alembic_cfg, str(self.migrations_dir / "alembic"))

        # Update env.py to use our Base
        env_py = self.migrations_dir / "alembic" / "env.py"
        env_content = env_py.read_text()
        env_content = env_content.replace(
            "target_metadata = None",
            "from migration_tool import Base\ntarget_metadata = Base.metadata"
        )
        env_py.write_text(env_content)

        click.echo(f"{Fore.GREEN}✓ Alembic initialized")

    def create_migration(self, message: str, auto: bool = True) -> Optional[str]:
        """Create a new Alembic migration"""
        try:
            alembic_ini = self.migrations_dir / "alembic.ini"
            if not alembic_ini.exists():
                click.echo(f"{Fore.RED}✗ Alembic not initialized. Run 'init' first.")
                return None

            alembic_cfg = Config(str(alembic_ini))

            if auto:
                # Auto-generate migration from model changes
                command.revision(alembic_cfg, message=message, autogenerate=True)
            else:
                # Create empty migration template
                command.revision(alembic_cfg, message=message)

            click.echo(f"{Fore.GREEN}✓ Migration created: {message}")
            return message
        except Exception as e:
            click.echo(f"{Fore.RED}✗ Failed to create migration: {e}")
            return None

    def validate_migration(self, migration_path: Path) -> Tuple[bool, str]:
        """Validate migration file syntax and structure"""
        try:
            with open(migration_path, 'r') as f:
                content = f.read()

            # Check for required functions
            if 'def upgrade' not in content:
                return False, "Missing upgrade() function"
            if 'def downgrade' not in content:
                return False, "Missing downgrade() function"

            # Try to compile the Python code
            compile(content, str(migration_path), 'exec')

            return True, "Valid migration file"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"

    def _calculate_checksum(self, migration_path: Path) -> str:
        """Calculate SHA256 checksum of migration file"""
        with open(migration_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def apply_migrations(self, dry_run: bool = False) -> bool:
        """Apply pending migrations with validation"""
        try:
            click.echo(f"\n{Fore.CYAN}=== Migration Application ==={Style.RESET_ALL}")

            if dry_run:
                click.echo(f"{Fore.YELLOW}DRY RUN MODE - No changes will be applied")

            # Check current database state
            current_version = self._get_current_alembic_version()
            click.echo(f"Current version: {current_version or 'None'}")

            # Get pending migrations
            pending = self._get_pending_migrations()

            if not pending:
                click.echo(f"{Fore.GREEN}✓ Database is up to date")
                return True

            click.echo(f"\nPending migrations: {len(pending)}")
            for version, desc in pending:
                click.echo(f"  - {version}: {desc}")

            if dry_run:
                click.echo(f"\n{Fore.YELLOW}Dry run complete. Use --apply to execute.")
                return True

            # Validate before applying
            click.echo(f"\n{Fore.CYAN}Validating migrations...")
            for version, desc in pending:
                migration_file = self._find_migration_file(version)
                if migration_file:
                    valid, msg = self.validate_migration(migration_file)
                    if not valid:
                        click.echo(f"{Fore.RED}✗ Validation failed for {version}: {msg}")
                        return False
                    click.echo(f"{Fore.GREEN}✓ {version} validated")

            # Apply migrations
            click.echo(f"\n{Fore.CYAN}Applying migrations...")
            alembic_ini = self.migrations_dir / "alembic.ini"
            alembic_cfg = Config(str(alembic_ini))

            command.upgrade(alembic_cfg, "head")

            click.echo(f"\n{Fore.GREEN}✓ All migrations applied successfully")
            return True

        except Exception as e:
            click.echo(f"{Fore.RED}✗ Migration failed: {e}")
            return False

    def rollback(self, steps: int = 1) -> bool:
        """Rollback migrations"""
        try:
            click.echo(f"\n{Fore.CYAN}=== Rolling Back {steps} Migration(s) ==={Style.RESET_ALL}")

            current = self._get_current_alembic_version()
            if not current:
                click.echo(f"{Fore.YELLOW}No migrations to rollback")
                return True

            # Confirm rollback
            click.echo(f"{Fore.YELLOW}WARNING: This will rollback {steps} migration(s)")
            if not click.confirm("Continue?"):
                click.echo("Rollback cancelled")
                return False

            alembic_ini = self.migrations_dir / "alembic.ini"
            alembic_cfg = Config(str(alembic_ini))

            # Calculate target version
            if steps == 1:
                target = "-1"
            else:
                target = f"-{steps}"

            command.downgrade(alembic_cfg, target)

            click.echo(f"{Fore.GREEN}✓ Rollback completed successfully")
            return True

        except Exception as e:
            click.echo(f"{Fore.RED}✗ Rollback failed: {e}")
            return False

    def status(self) -> Dict:
        """Get migration status"""
        try:
            current = self._get_current_alembic_version()
            pending = self._get_pending_migrations()
            applied = self._get_applied_migrations()

            return {
                'current_version': current,
                'pending_count': len(pending),
                'pending_migrations': pending,
                'applied_count': len(applied),
                'applied_migrations': applied
            }
        except Exception as e:
            click.echo(f"{Fore.RED}✗ Failed to get status: {e}")
            return {}

    def _get_current_alembic_version(self) -> Optional[str]:
        """Get current Alembic version from database"""
        try:
            with self.engine.connect() as conn:
                context = MigrationContext.configure(conn)
                return context.get_current_revision()
        except:
            return None

    def _get_pending_migrations(self) -> List[Tuple[str, str]]:
        """Get list of pending migrations"""
        try:
            alembic_ini = self.migrations_dir / "alembic.ini"
            alembic_cfg = Config(str(alembic_ini))
            script = ScriptDirectory.from_config(alembic_cfg)

            current = self._get_current_alembic_version()

            pending = []
            for rev in script.walk_revisions():
                if current is None or script.get_revision(current).revision == rev.revision:
                    break
                pending.append((rev.revision, rev.doc or "No description"))

            return list(reversed(pending))
        except:
            return []

    def _get_applied_migrations(self) -> List[Tuple[str, str, datetime]]:
        """Get list of applied migrations"""
        try:
            session = self.Session()
            migrations = session.query(MigrationHistory).order_by(
                MigrationHistory.applied_at
            ).all()
            session.close()

            return [(m.version, m.description, m.applied_at) for m in migrations]
        except:
            return []

    def _find_migration_file(self, version: str) -> Optional[Path]:
        """Find migration file by version"""
        alembic_versions = self.migrations_dir / "alembic" / "versions"
        if alembic_versions.exists():
            for file in alembic_versions.glob(f"*{version}*.py"):
                return file
        return None

    def create_custom_migration(self, name: str) -> Optional[Path]:
        """Create a custom migration template"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{name}.py"
            filepath = self.custom_migrations_dir / filename

            template = f'''"""
Custom Migration: {name}
Created: {datetime.now().isoformat()}
"""

def upgrade(engine):
    """
    Apply migration changes

    Args:
        engine: SQLAlchemy engine instance
    """
    with engine.connect() as conn:
        # Add your upgrade SQL here
        # Example:
        # conn.execute(text("""
        #     ALTER TABLE users ADD COLUMN email VARCHAR(255);
        # """))
        # conn.commit()
        pass


def downgrade(engine):
    """
    Rollback migration changes

    Args:
        engine: SQLAlchemy engine instance
    """
    with engine.connect() as conn:
        # Add your downgrade SQL here
        # Example:
        # conn.execute(text("""
        #     ALTER TABLE users DROP COLUMN email;
        # """))
        # conn.commit()
        pass


def validate(engine):
    """
    Validate migration can be applied safely

    Args:
        engine: SQLAlchemy engine instance

    Returns:
        tuple: (success: bool, message: str)
    """
    # Add validation logic here
    # Example: Check if table exists, column doesn't exist, etc.
    return True, "Validation passed"
'''

            filepath.write_text(template)
            click.echo(f"{Fore.GREEN}✓ Custom migration created: {filepath}")
            return filepath

        except Exception as e:
            click.echo(f"{Fore.RED}✗ Failed to create custom migration: {e}")
            return None

    def apply_custom_migrations(self, dry_run: bool = False) -> bool:
        """Apply custom migrations"""
        try:
            click.echo(f"\n{Fore.CYAN}=== Applying Custom Migrations ==={Style.RESET_ALL}")

            if not self.custom_migrations_dir.exists():
                click.echo(f"{Fore.YELLOW}No custom migrations directory")
                return True

            # Get all custom migration files
            migration_files = sorted(self.custom_migrations_dir.glob("*.py"))

            if not migration_files:
                click.echo(f"{Fore.GREEN}✓ No custom migrations to apply")
                return True

            session = self.Session()
            applied = {m.version for m in session.query(MigrationHistory.version).filter(
                MigrationHistory.migration_type == 'custom'
            ).all()}
            session.close()

            pending_files = [f for f in migration_files if f.stem not in applied]

            if not pending_files:
                click.echo(f"{Fore.GREEN}✓ All custom migrations already applied")
                return True

            click.echo(f"Found {len(pending_files)} pending custom migration(s)")

            for migration_file in pending_files:
                click.echo(f"\n{Fore.CYAN}Processing: {migration_file.name}")

                # Load migration module
                import importlib.util
                spec = importlib.util.spec_from_file_location("migration", migration_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Validate if function exists
                if hasattr(module, 'validate'):
                    valid, msg = module.validate(self.engine)
                    if not valid:
                        click.echo(f"{Fore.RED}✗ Validation failed: {msg}")
                        return False
                    click.echo(f"{Fore.GREEN}✓ Validation passed")

                if dry_run:
                    click.echo(f"{Fore.YELLOW}[DRY RUN] Would apply: {migration_file.name}")
                    continue

                # Apply migration
                try:
                    module.upgrade(self.engine)

                    # Record in history
                    session = self.Session()
                    history = MigrationHistory(
                        version=migration_file.stem,
                        description=migration_file.name,
                        migration_type='custom',
                        checksum=self._calculate_checksum(migration_file)
                    )
                    session.add(history)
                    session.commit()
                    session.close()

                    click.echo(f"{Fore.GREEN}✓ Applied: {migration_file.name}")

                except Exception as e:
                    click.echo(f"{Fore.RED}✗ Failed to apply {migration_file.name}: {e}")
                    return False

            if dry_run:
                click.echo(f"\n{Fore.YELLOW}Dry run complete. Use --apply to execute.")
            else:
                click.echo(f"\n{Fore.GREEN}✓ All custom migrations applied successfully")

            return True

        except Exception as e:
            click.echo(f"{Fore.RED}✗ Custom migration failed: {e}")
            return False


# CLI Interface
@click.group()
@click.option('--db-url', envvar='DATABASE_URL', required=True,
              help='Database URL (or set DATABASE_URL env var)')
@click.pass_context
def cli(ctx, db_url):
    """Database Migration Tool - Manage schema changes with confidence"""
    ctx.ensure_object(dict)
    ctx.obj['tool'] = DatabaseMigrationTool(db_url)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize migration system"""
    tool = ctx.obj['tool']
    tool.initialize()


@cli.command()
@click.argument('message')
@click.option('--auto/--manual', default=True, help='Auto-generate from models')
@click.pass_context
def create(ctx, message, auto):
    """Create a new migration"""
    tool = ctx.obj['tool']
    tool.create_migration(message, auto)


@cli.command()
@click.argument('name')
@click.pass_context
def create_custom(ctx, name):
    """Create a custom migration template"""
    tool = ctx.obj['tool']
    tool.create_custom_migration(name)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview without applying')
@click.pass_context
def upgrade(ctx, dry_run):
    """Apply pending migrations"""
    tool = ctx.obj['tool']
    tool.apply_migrations(dry_run=dry_run)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Preview without applying')
@click.pass_context
def upgrade_custom(ctx, dry_run):
    """Apply custom migrations"""
    tool = ctx.obj['tool']
    tool.apply_custom_migrations(dry_run=dry_run)


@cli.command()
@click.option('--steps', default=1, help='Number of migrations to rollback')
@click.pass_context
def downgrade(ctx, steps):
    """Rollback migrations"""
    tool = ctx.obj['tool']
    tool.rollback(steps)


@cli.command()
@click.pass_context
def status(ctx):
    """Show migration status"""
    tool = ctx.obj['tool']
    status = tool.status()

    click.echo(f"\n{Fore.CYAN}=== Migration Status ==={Style.RESET_ALL}\n")
    click.echo(f"Current Version: {status.get('current_version', 'None')}")
    click.echo(f"Applied Migrations: {status.get('applied_count', 0)}")
    click.echo(f"Pending Migrations: {status.get('pending_count', 0)}")

    if status.get('pending_migrations'):
        click.echo(f"\n{Fore.YELLOW}Pending:")
        for version, desc in status['pending_migrations']:
            click.echo(f"  → {version}: {desc}")

    if status.get('applied_migrations'):
        click.echo(f"\n{Fore.GREEN}Applied:")
        for version, desc, applied_at in status['applied_migrations'][-5:]:
            click.echo(f"  ✓ {version}: {desc} ({applied_at})")


if __name__ == '__main__':
    cli(obj={})
