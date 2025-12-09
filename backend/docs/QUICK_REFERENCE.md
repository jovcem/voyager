# Quick Reference Card

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Test database
python cli.py test

# Scrape and save
python cli.py scrape https://example.com/products --save-db

# List products
python cli.py list

# Run migrations
python cli.py migrate status
python cli.py migrate up
```

## Repository Usage

### Import and Initialize
```python
from repository import DatabaseRepository
repo = DatabaseRepository()
```

### Save Scraped Data (Most Common)
```python
products = [
    {'name': 'Product', 'price': 19.99, 'url': 'https://...'},
]
products_saved, prices_saved = repo.save_scraped_products(products, 'https://store.com')
```

### Query Data
```python
# Recent products
recent = repo.list_recent_products(limit=20)

# Search
results = repo.search_products('laptop', limit=50)

# Stats
stats = repo.get_stats()
print(f"Products: {stats['products']}, Prices: {stats['prices']}")
```

### Price History
```python
# Get history
history = repo.get_price_history(product_id=123, limit=30)

# Get latest
latest = repo.get_latest_price(product_id=123)
```

## Database Schema

```sql
stores (id, name, url, created_at)
  ↓
products (id, store_id, name, url, created_at)
  ↓
prices (id, product_id, price, currency, scraped_at)
```

## Scraper Template

```python
from repository import DatabaseRepository
import requests
from bs4 import BeautifulSoup

class MyScraper:
    def __init__(self):
        self.repo = DatabaseRepository()

    def scrape(self, url):
        # Fetch page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract products
        products = []
        for item in soup.select('.product'):
            products.append({
                'name': item.select_one('.name').text,
                'price': float(item.select_one('.price').text.strip('$')),
                'url': item.select_one('a')['href']
            })

        # Save to database
        saved, prices = self.repo.save_scraped_products(products, url)
        return products
```

## File Locations

- **Repository**: [repository.py](repository.py)
- **Full Guide**: [REPOSITORY_GUIDE.md](REPOSITORY_GUIDE.md)
- **Examples**: [example_repository_usage.py](example_repository_usage.py)
- **Getting Started**: [GETTING_STARTED.md](GETTING_STARTED.md)

## Database Connection

```python
# Environment variables in .env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=voyager
DATABASE_USER=voyager_user
DATABASE_PASSWORD=voyager_password
```

## Docker Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker logs voyager_postgres

# Access PostgreSQL shell
docker exec -it voyager_postgres psql -U voyager_user -d voyager
```

## Migration Workflow

```bash
# 1. Create migration file
# migrations/003_add_feature.sql

# 2. Write SQL
-- Up
ALTER TABLE products ADD COLUMN category VARCHAR(100);

-- Down
ALTER TABLE products DROP COLUMN category;

# 3. Apply migration
python cli.py migrate up

# 4. Rollback if needed
python cli.py migrate down
```
