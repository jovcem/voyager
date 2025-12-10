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
