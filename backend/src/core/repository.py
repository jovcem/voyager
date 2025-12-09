"""
Database Repository
Handles all database operations for stores, products, and prices
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
from .config import DB_CONFIG


class DatabaseRepository:
    """Repository for database operations"""

    def __init__(self, config: Dict = None):
        """
        Initialize repository with database configuration

        Args:
            config: Database configuration dict (uses DB_CONFIG if not provided)
        """
        self.config = config or DB_CONFIG

    def get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(**self.config)

    # Store operations

    def get_or_create_store(self, url: str) -> int:
        """
        Get existing store or create a new one

        Args:
            url: Store URL

        Returns:
            Store ID
        """
        # Extract domain as store name
        domain = urlparse(url).netloc
        store_name = domain.replace('www.', '')

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Try to find existing store
                cur.execute("SELECT id FROM stores WHERE name = %s", (store_name,))
                result = cur.fetchone()

                if result:
                    return result[0]

                # Create new store
                cur.execute(
                    "INSERT INTO stores (name, url) VALUES (%s, %s) RETURNING id",
                    (store_name, url)
                )
                store_id = cur.fetchone()[0]
                conn.commit()
                print(f"Created store: {store_name}")
                return store_id
        finally:
            conn.close()

    def get_store_by_id(self, store_id: int) -> Optional[Dict]:
        """
        Get store by ID

        Args:
            store_id: Store ID

        Returns:
            Store dictionary or None
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM stores WHERE id = %s", (store_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def list_stores(self) -> List[Dict]:
        """
        Get all stores

        Returns:
            List of store dictionaries
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM stores ORDER BY name")
                return cur.fetchall()
        finally:
            conn.close()

    # Product operations

    def get_or_create_product(self, store_id: int, name: str, url: str, image: str = None) -> int:
        """
        Get existing product or create a new one

        Args:
            store_id: Store ID
            name: Product name
            url: Product URL
            image: Product image URL (optional)

        Returns:
            Product ID
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Check if product exists by URL
                cur.execute(
                    "SELECT id FROM products WHERE store_id = %s AND url = %s",
                    (store_id, url)
                )
                result = cur.fetchone()

                if result:
                    product_id = result[0]
                    # Update image if provided
                    if image:
                        cur.execute(
                            "UPDATE products SET image = %s WHERE id = %s",
                            (image, product_id)
                        )
                        conn.commit()
                    return product_id

                # Create new product
                cur.execute(
                    "INSERT INTO products (store_id, name, url, image) VALUES (%s, %s, %s, %s) RETURNING id",
                    (store_id, name, url, image)
                )
                product_id = cur.fetchone()[0]
                conn.commit()
                return product_id
        finally:
            conn.close()

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Get product by ID

        Args:
            product_id: Product ID

        Returns:
            Product dictionary or None
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def update_product_name(self, product_id: int, name: str) -> bool:
        """
        Update product name

        Args:
            product_id: Product ID
            name: New product name

        Returns:
            True if successful
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET name = %s WHERE id = %s",
                    (name, product_id)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating product: {e}")
            return False
        finally:
            conn.close()

    # Price operations

    def add_price(self, product_id: int, price: float, currency: str = 'MKD') -> int:
        """
        Add a new price entry

        Args:
            product_id: Product ID
            price: Price value
            currency: Currency code (default: MKD)

        Returns:
            Price ID
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO prices (product_id, price, currency) VALUES (%s, %s, %s) RETURNING id",
                    (product_id, price, currency)
                )
                price_id = cur.fetchone()[0]
                conn.commit()
                return price_id
        finally:
            conn.close()

    def get_latest_price(self, product_id: int) -> Optional[Dict]:
        """
        Get the latest price for a product

        Args:
            product_id: Product ID

        Returns:
            Price dictionary or None
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM prices
                    WHERE product_id = %s
                    ORDER BY scraped_at DESC
                    LIMIT 1
                    """,
                    (product_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    def get_price_history(self, product_id: int, limit: int = 100) -> List[Dict]:
        """
        Get price history for a product

        Args:
            product_id: Product ID
            limit: Maximum number of records to return

        Returns:
            List of price dictionaries
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT * FROM prices
                    WHERE product_id = %s
                    ORDER BY scraped_at DESC
                    LIMIT %s
                    """,
                    (product_id, limit)
                )
                return cur.fetchall()
        finally:
            conn.close()

    # Batch operations

    def save_scraped_products(self, products: List[Dict], source_url: str) -> Tuple[int, int]:
        """
        Save multiple scraped products to database in a single transaction

        Args:
            products: List of product dictionaries with keys: name, price, url, image (optional)
            source_url: Source URL where products were scraped from

        Returns:
            Tuple of (products_saved, prices_saved)

        Example:
            products = [
                {'name': 'Product 1', 'price': 19.99, 'url': 'https://...', 'image': 'https://...'},
                {'name': 'Product 2', 'price': 29.99, 'url': 'https://...'},
            ]
            saved, prices = repo.save_scraped_products(products, 'https://store.com')
        """
        if not products:
            return 0, 0

        # Get or create store
        store_id = self.get_or_create_store(source_url)

        conn = self.get_connection()
        products_saved = 0
        prices_saved = 0

        try:
            with conn.cursor() as cur:
                for product in products:
                    try:
                        # Get or create product
                        cur.execute(
                            "SELECT id FROM products WHERE store_id = %s AND url = %s",
                            (store_id, product['url'])
                        )
                        result = cur.fetchone()

                        if result:
                            product_id = result[0]
                            # Update image if provided
                            image = product.get('image')
                            if image:
                                cur.execute(
                                    "UPDATE products SET image = %s WHERE id = %s",
                                    (image, product_id)
                                )
                        else:
                            cur.execute(
                                "INSERT INTO products (store_id, name, url, image) VALUES (%s, %s, %s, %s) RETURNING id",
                                (store_id, product['name'], product['url'], product.get('image'))
                            )
                            product_id = cur.fetchone()[0]
                            products_saved += 1

                        # Insert price
                        currency = product.get('currency', 'USD')
                        cur.execute(
                            "INSERT INTO prices (product_id, price, currency) VALUES (%s, %s, %s)",
                            (product_id, product['price'], currency)
                        )
                        prices_saved += 1

                    except Exception as e:
                        print(f"Error saving product '{product.get('name', 'unknown')}': {e}")
                        continue

            conn.commit()
            return products_saved, prices_saved

        except Exception as e:
            conn.rollback()
            print(f"Error in batch save: {e}")
            return 0, 0
        finally:
            conn.close()

    # Query operations

    def list_recent_products(self, limit: int = 20) -> List[Dict]:
        """
        Get recent products with their latest prices

        Args:
            limit: Number of products to return

        Returns:
            List of product dictionaries with store and price information
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.name,
                        p.url,
                        s.name as store,
                        pr.price,
                        pr.currency,
                        pr.scraped_at
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    JOIN prices pr ON p.id = pr.product_id
                    WHERE pr.id IN (
                        SELECT MAX(id)
                        FROM prices
                        GROUP BY product_id
                    )
                    ORDER BY pr.scraped_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                return cur.fetchall()
        finally:
            conn.close()

    def search_products(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search products by name

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of product dictionaries with latest prices
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.name,
                        p.url,
                        s.name as store,
                        pr.price,
                        pr.currency,
                        pr.scraped_at
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    LEFT JOIN LATERAL (
                        SELECT price, currency, scraped_at
                        FROM prices
                        WHERE product_id = p.id
                        ORDER BY scraped_at DESC
                        LIMIT 1
                    ) pr ON true
                    WHERE p.name ILIKE %s
                    ORDER BY pr.scraped_at DESC NULLS LAST
                    LIMIT %s
                    """,
                    (f'%{query}%', limit)
                )
                return cur.fetchall()
        finally:
            conn.close()

    # Utility operations

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test database connection

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
            conn.close()
            return True, f"Connected: {version.split(',')[0]}"
        except Exception as e:
            return False, f"Connection failed: {e}"

    def get_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with counts of stores, products, and prices
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM stores) as stores,
                        (SELECT COUNT(*) FROM products) as products,
                        (SELECT COUNT(*) FROM prices) as prices
                    """
                )
                return cur.fetchone()
        finally:
            conn.close()
