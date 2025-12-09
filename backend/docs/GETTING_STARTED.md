# Getting Started with Voyager

This guide will help you start using Voyager to scrape and track product prices.

## Quick Start

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Test Database Connection

```bash
python cli.py test
```

You should see:
```
✓ Database connection successful
PostgreSQL version: PostgreSQL 15.15
```

### 3. Check Migration Status

```bash
python cli.py migrate status
```

### 4. Scrape Your First Store

To scrape products from a store and save them to the database:

```bash
python cli.py scrape https://example-store.com/products --save-db
```

Without `--save-db`, it will only display results without saving.

### 5. View Your Data

```bash
python cli.py list
```

This shows the most recent products with their prices.

## How Data Gets Into the Database

There are **two ways** data enters your database:

### Method 1: Automatic via Scrapers (Recommended)

When you run a scrape command with `--save-db`:

```bash
python cli.py scrape https://neptun.hu --save-db
```

The scraper will:
1. Fetch the webpage
2. Extract products and prices
3. Automatically save everything to the database

**You don't need to manually insert data** - the scrapers do it for you!

### Method 2: Database Migrations (For Schema Changes)

Migrations are for **changing the database structure**, not inserting data.

Use migrations when you need to:
- Add new columns to tables
- Create new tables
- Modify existing table structures

Example migration workflow:

```bash
# Check what migrations are pending
python cli.py migrate status

# Apply pending migrations
python cli.py migrate up

# If something goes wrong, rollback
python cli.py migrate down
```

## Example Workflow

```bash
# 1. Start fresh
source venv/bin/activate

# 2. Test connection
python cli.py test

# 3. Scrape a store (this inserts data)
python cli.py scrape https://example.com/products --save-db

# 4. View the scraped data
python cli.py list

# 5. Scrape again later to track price changes
python cli.py scrape https://example.com/products --save-db
```

## Data Flow Diagram

```
Web Store → Scraper → Database
    ↓          ↓          ↓
  HTML    Extract    products table
           Data      prices table
                     stores table
```

## Common Commands

```bash
# See available commands
python cli.py --help

# Scrape and display (no save)
python cli.py scrape <url>

# Scrape and save to database
python cli.py scrape <url> --save-db

# List products with more results
python cli.py list --limit 50

# Check database status
python cli.py test

# Check migration status
python cli.py migrate status
```

## What About the Initial Migration?

The `001_initial.sql` migration is there for tracking purposes, but your database tables (`stores`, `products`, `prices`) are already created by `schema.sql` when the Docker container first started.

You can safely mark it as applied or leave it pending - it won't affect your scrapers.

## Next Steps

1. Try scraping different stores
2. Create site-specific scrapers in `scrapers/` directory (see `NeptunScraper.py` as example)
3. Schedule regular scrapes using cron or a task scheduler
4. Analyze price history using SQL queries
