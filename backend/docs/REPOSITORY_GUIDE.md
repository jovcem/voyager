# Repository Pattern Guide

## Overview

The `repository.py` module provides a clean, organized way to interact with the database. It separates data access logic from business logic, making your code more maintainable and testable.

## Quick Start

```python
from repository import DatabaseRepository

# Initialize the repository
repo = DatabaseRepository()

# Save scraped products
products = [
    {'name': 'Product 1', 'price': 19.99, 'url': 'https://store.com/p1'},
    {'name': 'Product 2', 'price': 29.99, 'url': 'https://store.com/p2'},
]
products_saved, prices_saved = repo.save_scraped_products(products, 'https://store.com')
```

## Architecture

```
┌─────────────────┐
│   CLI / App     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Scraper       │  ← Your scraping logic
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Repository    │  ← Data access layer (repository.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  ← Database
└─────────────────┘
```

## Key Benefits

1. **Separation of Concerns**: Database logic is separate from scraping logic
2. **Reusability**: Same repository methods can be used across different scrapers
3. **Testability**: Easy to mock for testing
4. **Type Safety**: Clear method signatures with type hints
5. **Transaction Management**: Handles database transactions automatically

## Common Use Cases

### 1. Saving Scraped Data (Most Common)

```python
from repository import DatabaseRepository

repo = DatabaseRepository()

# Your scraper returns a list of products
scraped_products = [
    {
        'name': 'Product Name',
        'price': 99.99,
        'url': 'https://example.com/product',
        'currency': 'USD'  # Optional, defaults to USD
    },
    # ... more products
]

# Save everything in one transaction
products_saved, prices_saved = repo.save_scraped_products(
    products=scraped_products,
    source_url='https://example.com/products'
)

print(f"Saved {products_saved} new products and {prices_saved} prices")
```

### 2. Manual Control (Advanced)

```python
# When you need more control over the process

# Step 1: Get or create the store
store_id = repo.get_or_create_store('https://example.com')

# Step 2: Get or create the product
product_id = repo.get_or_create_product(
    store_id=store_id,
    name='Product Name',
    url='https://example.com/product'
)

# Step 3: Add a price
price_id = repo.add_price(
    product_id=product_id,
    price=99.99,
    currency='USD'
)
```

### 3. Querying Data

```python
# Get recent products with latest prices
recent = repo.list_recent_products(limit=20)
for product in recent:
    print(f"{product['name']}: ${product['price']:.2f}")

# Search for products
results = repo.search_products('laptop', limit=50)

# Get price history for a product
history = repo.get_price_history(product_id=123, limit=30)
for record in history:
    print(f"{record['scraped_at']}: ${record['price']:.2f}")

# Get latest price for a product
latest = repo.get_latest_price(product_id=123)
print(f"Current price: ${latest['price']:.2f}")
```

### 4. Database Statistics

```python
# Get counts of all data
stats = repo.get_stats()
print(f"Stores: {stats['stores']}")
print(f"Products: {stats['products']}")
print(f"Prices: {stats['prices']}")

# Test connection
success, message = repo.test_connection()
if success:
    print(f"✓ {message}")
else:
    print(f"✗ {message}")
```

## Method Reference

### Store Operations

- `get_or_create_store(url: str) -> int`
  - Gets existing store or creates new one
  - Returns store ID

- `get_store_by_id(store_id: int) -> Optional[Dict]`
  - Gets store information by ID

- `list_stores() -> List[Dict]`
  - Gets all stores

### Product Operations

- `get_or_create_product(store_id: int, name: str, url: str) -> int`
  - Gets existing product or creates new one
  - Returns product ID

- `get_product_by_id(product_id: int) -> Optional[Dict]`
  - Gets product information by ID

- `update_product_name(product_id: int, name: str) -> bool`
  - Updates product name

### Price Operations

- `add_price(product_id: int, price: float, currency: str = 'USD') -> int`
  - Adds a new price record
  - Returns price ID

- `get_latest_price(product_id: int) -> Optional[Dict]`
  - Gets the most recent price for a product

- `get_price_history(product_id: int, limit: int = 100) -> List[Dict]`
  - Gets price history for a product

### Batch Operations

- `save_scraped_products(products: List[Dict], source_url: str) -> Tuple[int, int]`
  - Saves multiple products in one transaction
  - Returns (products_saved, prices_saved)

### Query Operations

- `list_recent_products(limit: int = 20) -> List[Dict]`
  - Gets recent products with latest prices

- `search_products(query: str, limit: int = 50) -> List[Dict]`
  - Searches products by name (case-insensitive)

### Utility Operations

- `test_connection() -> Tuple[bool, str]`
  - Tests database connection
  - Returns (success, message)

- `get_stats() -> Dict`
  - Gets database statistics
  - Returns counts of stores, products, and prices

## Integration with Scrapers

### Before (Direct Database Access)

```python
# Old way: scraper.py had database code mixed in
def save_products(products, url):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # ... lots of SQL code ...
    conn.commit()
    conn.close()
```

### After (Using Repository)

```python
# New way: scraper.py uses repository
from repository import DatabaseRepository

repo = DatabaseRepository()

def save_products(products, url):
    return repo.save_scraped_products(products, url)
```

Much cleaner and easier to maintain!

## Example: Creating a Custom Scraper

```python
from repository import DatabaseRepository
from bs4 import BeautifulSoup
import requests

class MyStoreScraper:
    def __init__(self):
        self.repo = DatabaseRepository()

    def scrape(self, url):
        # Fetch and parse HTML
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

        # Save to database using repository
        saved, prices = self.repo.save_scraped_products(products, url)
        print(f"Saved {saved} products, {prices} prices")

        return products

# Use it
scraper = MyStoreScraper()
scraper.scrape('https://mystore.com/products')
```

## Error Handling

The repository handles errors gracefully:

```python
try:
    products_saved, prices_saved = repo.save_scraped_products(products, url)
except Exception as e:
    print(f"Error saving products: {e}")
    # Repository will rollback the transaction automatically
```

## Testing with Repository

```python
# Create a test repository with test database
test_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'voyager_test',
    'user': 'test_user',
    'password': 'test_pass'
}

repo = DatabaseRepository(config=test_config)

# Now you can test without affecting production data
products_saved, prices_saved = repo.save_scraped_products(test_data, test_url)
assert products_saved == 5
```

## Best Practices

1. **Use batch operations**: `save_scraped_products()` is more efficient than calling individual methods
2. **Let repository handle transactions**: Don't manage connections manually
3. **Use type hints**: Makes code more maintainable
4. **Handle errors appropriately**: Repository methods raise exceptions on critical errors
5. **Reuse repository instance**: Create one instance and reuse it

## Examples

See [example_repository_usage.py](example_repository_usage.py) for complete working examples.

## Comparison: Old vs New

| Aspect | Old (Direct SQL) | New (Repository) |
|--------|-----------------|------------------|
| Code lines | ~100 lines | ~10 lines |
| SQL visibility | Everywhere | Hidden in repository |
| Reusability | Copy-paste | Import and use |
| Testability | Hard to mock | Easy to mock |
| Maintainability | Scattered logic | Centralized |
| Error handling | Manual | Automatic |

## Next Steps

1. Use the repository in your custom scrapers
2. Add new methods to repository as needed
3. Write tests using a test database
4. Consider adding caching for frequently accessed data
