"""
Scrapers module

This module contains all site-specific scrapers.
Each scraper inherits from BaseScraper and implements site-specific parsing logic.
"""
from .base import BaseScraper
from .neptun import NeptunScraper

# Registry of all available scrapers
# Add new scrapers here as you create them
SCRAPERS = [
    NeptunScraper,
    # Add more scrapers here:
    # MySiteScraper,
    # OtherSiteScraper,
]


def get_scraper_for_url(url):
    """
    Get the appropriate scraper for a given URL

    Args:
        url: URL to scrape

    Returns:
        BaseScraper subclass or None if no scraper found
    """
    for scraper_class in SCRAPERS:
        if scraper_class.can_handle(url):
            return scraper_class

    # Return None if no specific scraper found
    return None


__all__ = [
    'BaseScraper',
    'NeptunScraper',
    'SCRAPERS',
    'get_scraper_for_url',
]
