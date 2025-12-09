"""
Simple web scraper for price tracking
Fetches HTML and extracts product information
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .repository import DatabaseRepository

# Initialize repository
repo = DatabaseRepository()


def scrape_url(url):
    """
    Scrape a URL and extract product information
    Uses site-specific scrapers when available, falls back to generic scraper

    Args:
        url: URL to scrape

    Returns:
        List of product dictionaries with name, price, url
    """
    from ..scrapers import get_scraper_for_url

    # Try to get a site-specific scraper
    scraper_class = get_scraper_for_url(url)

    if scraper_class:
        print(f"Using {scraper_class.__name__} for {url}")
        scraper = scraper_class(url)
        return scraper.scrape()
    else:
        print(f"No specific scraper found for {url}, using generic scraper")
        return _generic_scrape(url)


def _generic_scrape(url):
    """
    Generic scraper for sites without specific scrapers

    Args:
        url: URL to scrape

    Returns:
        List of product dictionaries with name, price, url
    """
    print(f"Fetching {url}...")

    try:
        # Fetch HTML
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract products - these selectors will need to be adjusted per site
        # This is a generic approach that looks for common patterns
        products = []

        # Try to find product containers (common class names)
        product_containers = (
            soup.find_all('div', class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['product', 'item', 'card']
            )) or
            soup.find_all('article') or
            soup.find_all('li', class_=lambda x: x and 'product' in x.lower())
        )

        print(f"Found {len(product_containers)} potential product containers")

        for container in product_containers[:50]:  # Limit to first 50
            try:
                # Try to find product name
                name = None
                name_elem = (
                    container.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and 'title' in x.lower()) or
                    container.find(['h1', 'h2', 'h3', 'h4']) or
                    container.find(class_=lambda x: x and 'name' in x.lower()) or
                    container.find('a', class_=lambda x: x and 'title' in x.lower())
                )
                if name_elem:
                    name = name_elem.get_text(strip=True)

                # Try to find price
                price = None
                price_elem = (
                    container.find(class_=lambda x: x and 'price' in x.lower()) or
                    container.find('span', class_=lambda x: x and 'price' in x.lower()) or
                    container.find('div', class_=lambda x: x and 'price' in x.lower())
                )
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract numeric price (remove currency symbols)
                    import re
                    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                    if price_match:
                        price = float(price_match.group())

                # Try to find product URL
                product_url = None
                link = container.find('a', href=True)
                if link:
                    product_url = urljoin(url, link['href'])

                # Only add if we found at least name and price
                if name and price:
                    products.append({
                        'name': name,
                        'price': price,
                        'url': product_url or url
                    })

            except Exception as e:
                # Skip products that fail to parse
                continue

        print(f"Successfully extracted {len(products)} products")
        return products

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    except Exception as e:
        print(f"Error parsing page: {e}")
        return []


def save_products(products, url):
    """
    Save scraped products to database using repository

    Args:
        products: List of product dictionaries
        url: Source URL

    Returns:
        Number of products saved
    """
    if not products:
        print("No products to save")
        return 0

    # Use repository to save products
    products_saved, prices_saved = repo.save_scraped_products(products, url)
    print(f"Saved {products_saved} new products and {prices_saved} prices to database")
    return prices_saved


def list_products(limit=20):
    """
    List recent products from database using repository

    Args:
        limit: Number of products to return

    Returns:
        List of products with latest prices
    """
    return repo.list_recent_products(limit)
