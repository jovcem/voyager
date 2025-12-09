#!/usr/bin/env python3
"""
Database Migration Tool
Simple migration system for Voyager database schema changes
"""
import os
import sys
import re
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pathlib import Path

# Add parent directory to path to import from src
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.core.config import DB_CONFIG

MIGRATIONS_DIR = backend_dir / 'db' / 'migrations'


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)


def create_migrations_table():
    """Create the schema_migrations table if it doesn't exist"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("✓ Migrations table ready")
    finally:
        conn.close()


def get_applied_migrations():
    """Get list of applied migration versions"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM schema_migrations ORDER BY version")
            return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def get_migration_files():
    """Get sorted list of migration files"""
    if not MIGRATIONS_DIR.exists():
        return []

    files = []
    for f in MIGRATIONS_DIR.glob('*.sql'):
        if f.name != 'README.md':
            files.append(f)

    return sorted(files)


def parse_migration(file_path):
    """Parse a migration file into up and down sections"""
    content = file_path.read_text()

    # Split by -- Up and -- Down comments
    up_match = re.search(r'--\s*Up\s*\n(.*?)(?:--\s*Down|$)', content, re.DOTALL | re.IGNORECASE)
    down_match = re.search(r'--\s*Down\s*\n(.*?)$', content, re.DOTALL | re.IGNORECASE)

    up_sql = up_match.group(1).strip() if up_match else ""
    down_sql = down_match.group(1).strip() if down_match else ""

    return up_sql, down_sql


def apply_migration(file_path):
    """Apply a migration"""
    version = file_path.stem  # filename without extension
    up_sql, _ = parse_migration(file_path)

    if not up_sql:
        print(f"⚠ Warning: No UP section found in {file_path.name}")
        return False

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Execute the migration
            cur.execute(up_sql)

            # Record the migration
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (version,)
            )

        conn.commit()
        print(f"✓ Applied: {version}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"✗ Failed to apply {version}: {e}")
        return False
    finally:
        conn.close()


def rollback_migration(file_path):
    """Rollback a migration"""
    version = file_path.stem
    _, down_sql = parse_migration(file_path)

    if not down_sql:
        print(f"⚠ Warning: No DOWN section found in {file_path.name}")
        return False

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Execute the rollback
            cur.execute(down_sql)

            # Remove the migration record
            cur.execute(
                "DELETE FROM schema_migrations WHERE version = %s",
                (version,)
            )

        conn.commit()
        print(f"✓ Rolled back: {version}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"✗ Failed to rollback {version}: {e}")
        return False
    finally:
        conn.close()


def migrate_up():
    """Apply all pending migrations"""
    create_migrations_table()

    applied = get_applied_migrations()
    migration_files = get_migration_files()

    if not migration_files:
        print("No migration files found in migrations/")
        return

    pending = [f for f in migration_files if f.stem not in applied]

    if not pending:
        print("✓ All migrations are up to date")
        return

    print(f"\nApplying {len(pending)} pending migration(s)...\n")

    for migration_file in pending:
        if not apply_migration(migration_file):
            print("\n✗ Migration failed, stopping")
            sys.exit(1)

    print(f"\n✓ Successfully applied {len(pending)} migration(s)")


def migrate_down():
    """Rollback the last applied migration"""
    create_migrations_table()

    applied = get_applied_migrations()

    if not applied:
        print("No migrations to rollback")
        return

    last_version = applied[-1]
    migration_file = MIGRATIONS_DIR / f"{last_version}.sql"

    if not migration_file.exists():
        print(f"✗ Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"\nRolling back migration: {last_version}\n")

    if rollback_migration(migration_file):
        print("\n✓ Rollback successful")
    else:
        print("\n✗ Rollback failed")
        sys.exit(1)


def show_status():
    """Show migration status"""
    create_migrations_table()

    applied = get_applied_migrations()
    migration_files = get_migration_files()

    print("\nMigration Status:\n")
    print(f"Applied migrations: {len(applied)}")
    print(f"Total migrations: {len(migration_files)}\n")

    if migration_files:
        print("Migrations:")
        for f in migration_files:
            status = "✓ Applied" if f.stem in applied else "○ Pending"
            print(f"  {status}  {f.name}")
    else:
        print("No migration files found")

    print()


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [up|down|status]")
        print()
        print("Commands:")
        print("  up      - Apply all pending migrations")
        print("  down    - Rollback the last migration")
        print("  status  - Show migration status")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == 'up':
            migrate_up()
        elif command == 'down':
            migrate_down()
        elif command == 'status':
            show_status()
        else:
            print(f"Unknown command: {command}")
            print("Use: up, down, or status")
            sys.exit(1)
    except psycopg2.OperationalError as e:
        print(f"✗ Database connection failed: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL container is running: docker-compose up -d")
        print("  2. Database credentials in .env are correct")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
