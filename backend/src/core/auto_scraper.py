"""
Auto scraper - automatically scrapes all configured providers
Reads scrape.json files from each provider folder and executes scraping
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple
from .scraper import scrape_url, save_products


def discover_scrape_configs() -> List[Tuple[str, Path]]:
    """
    Discover all scrape.json files in provider folders

    Returns:
        List of (provider_name, config_path) tuples
    """
    scrapers_dir = Path(__file__).parent.parent / 'scrapers'
    configs = []

    for provider_dir in scrapers_dir.iterdir():
        # Skip __pycache__ and non-directories
        if provider_dir.is_dir() and not provider_dir.name.startswith('__'):
            config_path = provider_dir / 'scrape.json'
            if config_path.exists():
                configs.append((provider_dir.name, config_path))

    return configs


def load_scrape_config(config_path: Path) -> List[Dict]:
    """
    Load and parse a scrape.json file

    Args:
        config_path: Path to scrape.json

    Returns:
        List of scrape target dictionaries
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_auto_scraper(save_to_db: bool = True) -> Dict:
    """
    Run auto scraper on all configured providers

    Args:
        save_to_db: Whether to save scraped products to database

    Returns:
        Dictionary with scraping results
    """
    print("🤖 Starting auto scraper...")
    print("=" * 60)

    # Discover all provider configurations
    configs = discover_scrape_configs()
    print(f"\n📁 Found {len(configs)} provider(s) with scrape configs\n")

    results = {
        'total_providers': len(configs),
        'total_urls': 0,
        'successful_scrapes': 0,
        'failed_scrapes': 0,
        'total_products': 0,
        'details': []
    }

    # Process each provider
    for provider_name, config_path in configs:
        print(f"📦 Provider: {provider_name}")
        print(f"   Config: {config_path.name}")

        try:
            # Load configuration
            scrape_targets = load_scrape_config(config_path)

            # Filter enabled targets
            enabled_targets = [t for t in scrape_targets if t.get('enabled', False)]
            print(f"   Enabled targets: {len(enabled_targets)}/{len(scrape_targets)}\n")

            results['total_urls'] += len(enabled_targets)

            # Scrape each target
            for target in enabled_targets:
                url = target.get('url')
                category = target.get('category', 'unknown')
                description = target.get('description', 'No description')

                print(f"   🔍 {description}")
                print(f"      Category: {category}")
                print(f"      URL: {url}")

                try:
                    # Scrape the URL with category
                    products = scrape_url(url, category=category)

                    if products:
                        print(f"      ✓ Found {len(products)} products")

                        # Save to database if requested
                        if save_to_db:
                            saved_count = save_products(products, url, category=category)
                            print(f"      ✓ Saved {saved_count} products to database")

                        results['successful_scrapes'] += 1
                        results['total_products'] += len(products)

                        results['details'].append({
                            'provider': provider_name,
                            'category': category,
                            'url': url,
                            'status': 'success',
                            'products_found': len(products)
                        })
                    else:
                        print(f"      ⚠ No products found")
                        results['failed_scrapes'] += 1
                        results['details'].append({
                            'provider': provider_name,
                            'category': category,
                            'url': url,
                            'status': 'no_products',
                            'products_found': 0
                        })

                except Exception as e:
                    print(f"      ✗ Error: {e}")
                    results['failed_scrapes'] += 1
                    results['details'].append({
                        'provider': provider_name,
                        'category': category,
                        'url': url,
                        'status': 'error',
                        'error': str(e)
                    })

                print()  # Empty line between targets

        except Exception as e:
            print(f"   ✗ Error loading config: {e}\n")
            continue

    # Print summary
    print("=" * 60)
    print("📊 SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Providers processed: {results['total_providers']}")
    print(f"URLs attempted: {results['total_urls']}")
    print(f"Successful scrapes: {results['successful_scrapes']}")
    print(f"Failed scrapes: {results['failed_scrapes']}")
    print(f"Total products found: {results['total_products']}")
    print("=" * 60)

    return results
