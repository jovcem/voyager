#!/usr/bin/env python3
"""
Example: How to use the DatabaseRepository to save scraped data

This shows different ways to interact with the database using the repository pattern.
"""
import sys
from pathlib import Path

# Add parent directory to path to import from src
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.core.repository import DatabaseRepository

# Initialize the repository
repo = DatabaseRepository()


def example_1_save_scraped_products():
    """
    Example 1: Save scraped products in batch (most common use case)
    """
    print("=" * 60)
    print("Example 1: Batch save scraped products")
    print("=" * 60)

    # Simulated scraped data
    scraped_products = [
        {
            'name': 'Laptop HP ProBook 450',
            'price': 899.99,
            'url': 'https://example.com/laptop-hp-450',
            'currency': 'USD'
        },
        {
            'name': 'Mouse Logitech MX Master 3',
            'price': 99.99,
            'url': 'https://example.com/mouse-logitech-mx3',
            'currency': 'USD'
        },
        {
            'name': 'Keyboard Mechanical RGB',
            'price': 149.99,
            'url': 'https://example.com/keyboard-rgb',
            'currency': 'USD'
        }
    ]

    # Save all products at once
    source_url = 'https://example.com/products'
    products_saved, prices_saved = repo.save_scraped_products(scraped_products, source_url)

    print(f"✓ Saved {products_saved} new products")
    print(f"✓ Saved {prices_saved} prices")
    print()


def example_2_manual_save():
    """
    Example 2: Manually save products one by one (more control)
    """
    print("=" * 60)
    print("Example 2: Manual save with full control")
    print("=" * 60)

    # Get or create store
    store_id = repo.get_or_create_store('https://techstore.com')
    print(f"Store ID: {store_id}")

    # Get or create product
    product_id = repo.get_or_create_product(
        store_id=store_id,
        name='Monitor Dell 27" 4K',
        url='https://techstore.com/monitor-dell-27'
    )
    print(f"Product ID: {product_id}")

    # Add price
    price_id = repo.add_price(
        product_id=product_id,
        price=499.99,
        currency='USD'
    )
    print(f"Price ID: {price_id}")
    print()


def example_3_query_data():
    """
    Example 3: Query and retrieve data
    """
    print("=" * 60)
    print("Example 3: Query database")
    print("=" * 60)

    # Get recent products
    recent = repo.list_recent_products(limit=5)
    print(f"\nRecent products ({len(recent)}):")
    for p in recent:
        print(f"  - {p['name']}: ${p['price']:.2f} ({p['store']})")

    # Search products
    search_results = repo.search_products('laptop', limit=10)
    print(f"\nSearch results for 'laptop' ({len(search_results)}):")
    for p in search_results:
        print(f"  - {p['name']}: ${p['price']:.2f}")

    # Get database stats
    stats = repo.get_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Stores: {stats['stores']}")
    print(f"  Products: {stats['products']}")
    print(f"  Prices: {stats['prices']}")
    print()


def example_4_price_history():
    """
    Example 4: Track price history for a product
    """
    print("=" * 60)
    print("Example 4: Price history")
    print("=" * 60)

    # First, let's add some price history
    store_id = repo.get_or_create_store('https://example.com')
    product_id = repo.get_or_create_product(
        store_id=store_id,
        name='iPhone 15 Pro',
        url='https://example.com/iphone-15-pro'
    )

    # Simulate multiple price scrapes over time
    prices = [1099.99, 1049.99, 999.99, 1029.99]
    for price in prices:
        repo.add_price(product_id, price, 'MKD')

    # Get price history
    history = repo.get_price_history(product_id, limit=10)
    print(f"\nPrice history for product {product_id}:")
    for record in history:
        print(f"  ${record['price']:.2f} - {record['scraped_at']}")

    # Get latest price
    latest = repo.get_latest_price(product_id)
    print(f"\nLatest price: ${latest['price']:.2f}")
    print()


def example_5_integration_with_scraper():
    """
    Example 5: How scrapers use the repository
    """
    print("=" * 60)
    print("Example 5: Integration with scraper")
    print("=" * 60)

    # This is what your scraper does:
    def scrape_website(url):
        """Simulated scraper function"""
        # In real scraper, this would fetch and parse HTML
        return [
            {'name': 'Product A', 'price': 29.99, 'url': f'{url}/product-a'},
            {'name': 'Product B', 'price': 39.99, 'url': f'{url}/product-b'},
        ]

    # Scrape the website
    url = 'https://mystore.com/products'
    products = scrape_website(url)

    # Save to database using repository
    products_saved, prices_saved = repo.save_scraped_products(products, url)

    print(f"Scraped {len(products)} products from {url}")
    print(f"Saved {products_saved} new products and {prices_saved} prices")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("DATABASE REPOSITORY USAGE EXAMPLES")
    print("=" * 60 + "\n")

    # Test connection first
    success, message = repo.test_connection()
    if not success:
        print(f"❌ Database connection failed: {message}")
        print("Make sure PostgreSQL is running: docker-compose up -d")
        exit(1)

    print(f"✓ {message}\n")

    # Run examples
    try:
        example_1_save_scraped_products()
        example_2_manual_save()
        example_3_query_data()
        example_4_price_history()
        example_5_integration_with_scraper()

        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
