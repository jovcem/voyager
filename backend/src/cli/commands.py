#!/usr/bin/env python3
"""
Voyager Price Scraper CLI
Simple command-line interface for scraping prices
"""
import click
import json
import sys
from ..core.scraper import scrape_url, save_products, list_products
from ..core.auto_scraper import run_auto_scraper
from tabulate import tabulate


@click.group()
@click.version_option(version="1.0.0", prog_name="Voyager Scraper")
def cli():
    """Voyager Price Scraper - Track prices from online stores"""
    pass


@cli.command()
@click.argument('url')
@click.option('--save-db', is_flag=True, help='Save products to database')
@click.option('--output', '-o', type=click.Choice(['table', 'json'], case_sensitive=False),
              default='table', help='Output format (table or json)')
@click.option('--save-json', type=click.Path(), help='Save results to JSON file')
def scrape(url, save_db, output, save_json):
    """
    Scrape products from a URL and display them

    Example:
        python cli.py scrape https://example.com/products
        python cli.py scrape https://example.com/products --save-db
        python cli.py scrape https://example.com/products --output json
        python cli.py scrape https://example.com/products --save-json results.json
    """
    click.echo(f"Scraping {url}...\n")

    # Scrape the URL
    products = scrape_url(url)

    if not products:
        click.echo("No products found. The page might use different HTML structure.", err=True)
        click.echo("Try a different URL or adjust the scraper selectors.")
        return

    # Display based on output format
    if output == 'json':
        # Output as JSON
        json_output = json.dumps(products, indent=2, ensure_ascii=False)
        click.echo(json_output)
    else:
        # Display what we found
        click.echo(f"\nFound {len(products)} products:\n")

        # Show all products in a table format
        table_data = []
        for i, product in enumerate(products, 1):
            table_data.append([
                i,
                product['name'][:60] + '...' if len(product['name']) > 60 else product['name'],
                product['price'],
                product['url'][:50] + '...' if len(product['url']) > 50 else product['url']
            ])

        headers = ['#', 'Product Name', 'Price', 'URL']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\nTotal: {len(products)} products found")

    # Save to JSON file if requested
    if save_json:
        try:
            with open(save_json, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            click.echo(f"\n✓ Saved {len(products)} products to {save_json}")
        except Exception as e:
            click.echo(f"\n✗ Error saving to JSON: {e}", err=True)

    # Save to database only if flag is set
    if save_db:
        click.echo("\nSaving to database...")
        saved_count = save_products(products, url)
        if saved_count > 0:
            click.echo(f"✓ Successfully saved {saved_count} products")
        else:
            click.echo("⚠ No products were saved", err=True)


@cli.command()
@click.option('--limit', '-l', default=20, help='Number of products to show')
def list(limit):
    """
    List recent products from database

    Example:
        python cli.py list
        python cli.py list --limit 50
    """
    products = list_products(limit)

    if not products:
        click.echo("No products found in database.")
        click.echo("Use 'python cli.py scrape <url>' to add products.")
        return

    # Format as table
    table_data = []
    for product in products:
        table_data.append([
            product['name'][:50] + '...' if len(product['name']) > 50 else product['name'],
            product['store'],
            f"${product['price']:.2f}",
            product['scraped_at'].strftime('%Y-%m-%d %H:%M')
        ])

    headers = ['Product', 'Store', 'Price', 'Scraped At']
    click.echo(f"\nLatest {len(products)} products:\n")
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@cli.command()
def test():
    """Test database connection"""
    try:
        from ..core.repository import DatabaseRepository
        repo = DatabaseRepository()
        success, message = repo.test_connection()

        if success:
            click.echo("✓ Database connection successful")
            click.echo(f"PostgreSQL version: {message.replace('Connected: ', '')}")

            # Show stats
            stats = repo.get_stats()
            click.echo(f"\nDatabase stats:")
            click.echo(f"  Stores: {stats['stores']}")
            click.echo(f"  Products: {stats['products']}")
            click.echo(f"  Prices: {stats['prices']}")
        else:
            click.echo(f"✗ {message}", err=True)
    except Exception as e:
        click.echo(f"✗ Database connection failed: {e}", err=True)


@cli.command()
@click.argument('action', type=click.Choice(['up', 'down', 'status'], case_sensitive=False))
def migrate(action):
    """
    Run database migrations

    Example:
        python cli.py migrate status
        python cli.py migrate up
        python cli.py migrate down
    """
    import subprocess
    import os
    # Get the backend directory (parent of src/)
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    migrate_script = os.path.join(backend_dir, 'scripts', 'migrate.py')
    result = subprocess.run(['python', migrate_script, action], capture_output=False)
    sys.exit(result.returncode)


@cli.command('scrape-by')
@click.option('--provider', '-p', required=True, help='Provider name (e.g., neptun)')
@click.option('--category', '-c', help='Category slug (e.g., gpu, motherboard)')
@click.option('--save-db/--no-save-db', default=True, help='Save products to database (default: True)')
@click.option('--output', '-o', type=click.Choice(['table', 'json'], case_sensitive=False),
              default='table', help='Output format')
def scrape_by(provider, category, save_db, output):
    """
    Scrape by provider name and optionally filter by category

    Reads scrape.json from the provider folder and scrapes matching URLs.

    Example:
        python cli.py scrape-by --provider neptun --category gpu
        python cli.py scrape-by -p neptun -c motherboard
        python cli.py scrape-by -p neptun
    """
    from pathlib import Path
    import json

    # Find provider folder
    scrapers_dir = Path(__file__).parent.parent / 'scrapers'
    provider_dir = scrapers_dir / provider

    if not provider_dir.exists():
        click.echo(f"✗ Provider '{provider}' not found", err=True)
        click.echo(f"\nAvailable providers:")
        for p in scrapers_dir.iterdir():
            if p.is_dir() and not p.name.startswith('__'):
                click.echo(f"  - {p.name}")
        sys.exit(1)

    # Load scrape.json
    config_path = provider_dir / 'scrape.json'
    if not config_path.exists():
        click.echo(f"✗ No scrape.json found in {provider} folder", err=True)
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            scrape_targets = json.load(f)
    except Exception as e:
        click.echo(f"✗ Error loading scrape.json: {e}", err=True)
        sys.exit(1)

    # Filter by category if provided
    if category:
        scrape_targets = [t for t in scrape_targets if t.get('category') == category]
        if not scrape_targets:
            click.echo(f"✗ No targets found for category '{category}' in {provider}", err=True)
            click.echo(f"\nAvailable categories:")
            with open(config_path, 'r', encoding='utf-8') as f:
                all_targets = json.load(f)
                categories = set(t.get('category', 'unknown') for t in all_targets)
                for cat in sorted(categories):
                    click.echo(f"  - {cat}")
            sys.exit(1)

    # Filter enabled targets
    enabled_targets = [t for t in scrape_targets if t.get('enabled', False)]

    if not enabled_targets:
        click.echo(f"✗ No enabled targets found", err=True)
        sys.exit(1)

    click.echo(f"🔍 Scraping {provider} - {len(enabled_targets)} target(s)")
    if category:
        click.echo(f"   Category: {category}")
    click.echo()

    all_products = []

    # Scrape each target
    for target in enabled_targets:
        url = target.get('url')
        target_category = target.get('category')
        description = target.get('description', 'No description')

        click.echo(f"📦 {description}")
        click.echo(f"   Category: {target_category}")
        click.echo(f"   URL: {url}")

        try:
            # Scrape the URL
            products = scrape_url(url, category=target_category)

            if products:
                click.echo(f"   ✓ Found {len(products)} products")
                all_products.extend(products)

                # Save to database if requested
                if save_db:
                    saved_count = save_products(products, url, category=target_category)
                    click.echo(f"   ✓ Saved {saved_count} products to database")
            else:
                click.echo(f"   ⚠ No products found")

        except Exception as e:
            click.echo(f"   ✗ Error: {e}", err=True)

        click.echo()

    # Summary
    click.echo("=" * 60)
    click.echo(f"📊 SUMMARY")
    click.echo(f"Total products found: {len(all_products)}")
    click.echo("=" * 60)

    # Display results
    if all_products and output == 'table':
        click.echo("\nProducts:\n")
        table_data = []
        for i, product in enumerate(all_products[:50], 1):  # Limit display to 50
            table_data.append([
                i,
                product['name'][:50] + '...' if len(product['name']) > 50 else product['name'],
                product['price'],
            ])

        headers = ['#', 'Product Name', 'Price']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))

        if len(all_products) > 50:
            click.echo(f"\n... and {len(all_products) - 50} more products")

    elif all_products and output == 'json':
        click.echo(json.dumps(all_products, indent=2, ensure_ascii=False))


@cli.command('auto-scrape')
@click.option('--save-db/--no-save-db', default=True, help='Save products to database (default: True)')
@click.option('--dry-run', is_flag=True, help='Run without saving to database')
def auto_scrape(save_db, dry_run):
    """
    Automatically scrape all configured providers

    Reads scrape.json files from each provider folder and executes scraping.

    Example:
        python cli.py auto-scrape
        python cli.py auto-scrape --dry-run
        python cli.py auto-scrape --no-save-db
    """
    # Dry run overrides save-db
    if dry_run:
        save_db = False
        click.echo("🔍 Running in DRY RUN mode (not saving to database)\n")

    try:
        results = run_auto_scraper(save_to_db=save_db)

        # Exit with error code if all scrapes failed
        if results['total_urls'] > 0 and results['successful_scrapes'] == 0:
            click.echo("\n❌ All scrapes failed", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Fatal error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()
