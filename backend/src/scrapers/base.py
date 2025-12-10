"""
Base scraper class for all site-specific scrapers
"""
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers

    Each site-specific scraper should:
    1. Inherit from this class
    2. Set the DOMAIN class variable
    3. Implement the parse_products() method
    """

    # Override this in subclasses to match the domain
    DOMAIN = None

    # Set to True in subclasses if the site requires JavaScript rendering
    REQUIRES_JAVASCRIPT = False

    def __init__(self, url, category=None):
        """
        Initialize the scraper

        Args:
            url: URL to scrape
            category: Category slug for products (optional)
        """
        self.url = url
        self.category = category
        self.soup = None
        self.products = []
        self.driver = None

    def fetch(self):
        """
        Fetch the HTML content from the URL
        Uses Selenium if REQUIRES_JAVASCRIPT is True, otherwise uses requests

        Returns:
            bool: True if successful, False otherwise
        """
        if self.REQUIRES_JAVASCRIPT:
            return self._fetch_with_selenium()
        else:
            return self._fetch_with_requests()

    def _fetch_with_requests(self):
        """
        Fetch HTML using requests (for static content)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"Fetching {self.url}...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            # Save HTML response to file for debugging
            self._save_response(response.text)

            self.soup = BeautifulSoup(response.text, 'html.parser')
            return True

        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return False

    def _fetch_with_selenium(self):
        """
        Fetch HTML using Selenium (for JavaScript-rendered content)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            print(f"Fetching {self.url} with Selenium (JavaScript enabled)...")

            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

            # Initialize the driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.url)

            # Wait for content to load (adjust wait time as needed)
            print("Waiting for JavaScript content to load...")
            time.sleep(5)  # Give time for dynamic content to load

            # Get the rendered HTML
            html_content = self.driver.page_source

            # Save HTML response to file for debugging
            self._save_response(html_content)

            self.soup = BeautifulSoup(html_content, 'html.parser')
            return True

        except Exception as e:
            print(f"Error fetching URL with Selenium: {e}")
            return False

    def _save_response(self, html_content):
        """
        Save HTML response to out folder for debugging

        Args:
            html_content: HTML content to save
        """
        import os
        from datetime import datetime

        # Create out folder if it doesn't exist
        out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'out')
        os.makedirs(out_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        class_name = self.__class__.__name__
        filename = f"{class_name}_{timestamp}.html"
        filepath = os.path.join(out_dir, filename)

        # Save HTML content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Saved HTML response to: {filepath}")

    @abstractmethod
    def parse_products(self):
        """
        Parse products from the page

        This method must be implemented by subclasses.
        Should populate self.products with a list of dictionaries:
        [
            {
                'name': 'Product Name',
                'price': 99.99,
                'url': 'https://example.com/product'
            },
            ...
        ]
        """
        pass

    def scrape(self):
        """
        Main scraping method - fetches and parses products

        Returns:
            list: List of product dictionaries
        """
        try:
            if not self.fetch():
                return []

            self.parse_products()

            print(f"Successfully extracted {len(self.products)} products")
            return self.products
        finally:
            # Clean up Selenium driver if it was used
            self._cleanup()

    def _cleanup(self):
        """Clean up resources (e.g., Selenium driver)"""
        if self.driver:
            try:
                self.driver.quit()
                print("Selenium driver closed")
            except Exception as e:
                print(f"Error closing Selenium driver: {e}")

    def _extract_price(self, price_text):
        """
        Helper method to extract numeric price from text

        Args:
            price_text: String containing price (e.g., "$99.99", "99,99 €")

        Returns:
            float: Extracted price or None
        """
        if not price_text:
            return None

        import re
        # Remove common currency symbols and spaces
        clean_text = price_text.replace('$', '').replace('€', '').replace('£', '').strip()
        # Handle both comma and dot as decimal separator
        clean_text = clean_text.replace(',', '.')
        # Extract numeric value
        price_match = re.search(r'\d+\.?\d*', clean_text)

        if price_match:
            return float(price_match.group())
        return None

    def _make_absolute_url(self, relative_url):
        """
        Convert relative URL to absolute URL

        Args:
            relative_url: Relative or absolute URL

        Returns:
            str: Absolute URL
        """
        return urljoin(self.url, relative_url)

    @classmethod
    def can_handle(cls, url):
        """
        Check if this scraper can handle the given URL

        Args:
            url: URL to check

        Returns:
            bool: True if this scraper can handle the URL
        """
        if cls.DOMAIN is None:
            return False
        return cls.DOMAIN in url.lower()
