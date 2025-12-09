# Database Migrations

This folder contains database migration scripts for schema changes.

## How Migrations Work

- Migrations are numbered SQL files (e.g., `001_initial.sql`, `002_add_column.sql`)
- They are applied in order to evolve the database schema
- A `schema_migrations` table tracks which migrations have been applied

## Running Migrations

```bash
# Run all pending migrations
python migrate.py up

# Rollback the last migration
python migrate.py down

# Check migration status
python migrate.py status
```

## Creating a New Migration

1. Create a new file: `migrations/XXX_description.sql` (increment the number)
2. Add your SQL changes with both UP and DOWN sections:

```sql
-- Migration: Add new column to products
-- Up
ALTER TABLE products ADD COLUMN category VARCHAR(100);

-- Down
ALTER TABLE products DROP COLUMN category;
```

## Notes

- The initial schema is in `schema.sql` and is automatically applied by Docker
- Migrations are for changes after the initial setup
- Always test migrations before applying to production
