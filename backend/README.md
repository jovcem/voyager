# Voyager Price Scraper

A simple Python web scraper for tracking product prices from online stores.

## Setup

### 1. Install Python Dependencies

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database

Start the PostgreSQL container with Docker:

```bash
docker-compose up -d
```

Check that it's running:

```bash
docker ps
```

### 3. Test Database Connection

```bash
python cli.py test
```

If successful, you'll see: `✓ Database connection successful`

## Usage

### Scrape a URL

```bash
python cli.py scrape <url>
```

Example:
```bash
python cli.py scrape https://example-store.com/products
```

The scraper will:
1. Fetch the page
2. Extract product names and prices
3. Save them to the database

### List Saved Products

```bash
python cli.py list
```

Show more results:
```bash
python cli.py list --limit 50
```

## Project Structure

```
backend/
├── cli.py                      # Command-line interface
├── scraper.py                  # Scraping logic
├── repository.py               # Database operations (NEW)
├── migrate.py                  # Database migrations
├── schema.sql                  # Database schema
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt            # Python dependencies
├── migrations/                 # Migration files
├── scrapers/                   # Site-specific scrapers
└── .env                       # Database credentials
```

## Repository Pattern

The project uses a repository pattern for database operations. Instead of writing SQL directly in your scrapers, use the `DatabaseRepository` class:

```python
from repository import DatabaseRepository

repo = DatabaseRepository()

# Save scraped products
products = [
    {'name': 'Product 1', 'price': 19.99, 'url': 'https://...'},
]
repo.save_scraped_products(products, source_url)
```

See [REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md) for complete documentation and examples.

## Database Schema

- **stores** - Store information (id, name, url)
- **products** - Products (id, store_id, name, url)
- **prices** - Price history (id, product_id, price, scraped_at)

## Database Migrations

The project includes a migration system for managing schema changes:

```bash
# Check migration status
python migrate.py status

# Apply all pending migrations
python migrate.py up

# Rollback the last migration
python migrate.py down
```

Migrations are stored in `migrations/` directory. See [migrations/README.md](migrations/README.md) for details on creating new migrations.

## Notes

- The scraper uses generic selectors that work with many sites
- For best results, you may need to adjust the selectors in `scraper.py`
- The database runs in Docker with memory optimized for 8GB RAM systems
- Prices are stored with full history - you can track price changes over time

## Stopping the Database

```bash
docker-compose down
```

## Next Steps

Once this is working, you can add:
- Site-specific scrapers with custom selectors
- Configuration files for multiple sites
- Scheduling (cron jobs)
- Export features (CSV, JSON)
- Error handling and retry logic
