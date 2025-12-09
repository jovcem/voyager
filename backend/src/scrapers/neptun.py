"""
Neptun-specific scraper
"""
from .base import BaseScraper


class NeptunScraper(BaseScraper):
    """
    Scraper for Neptun website

    Neptun uses JavaScript to dynamically load products,
    so we need Selenium to render the page.
    """

    # Set this to the Neptun domain (e.g., 'neptun.mk', 'neptun.com', etc.)
    DOMAIN = 'neptun'

    # Enable JavaScript rendering for Neptun
    REQUIRES_JAVASCRIPT = True

    def parse_products(self):
        """
        Parse products from Neptun website

        Selectors based on Neptun's HTML structure:
        - Product container: div.theProduct
        - Product name: h2 (inside productCardBody)
        - Price: span.priceNum (inside discountPrice)
        - Product URL: a (direct child of theProduct)
        """
        if not self.soup:
            return

        print(f"Parsing Neptun products from {self.url}...")

        # Find all product containers
        product_containers = self.soup.find_all('div', class_='theProduct')

        print(f"Found {len(product_containers)} product containers")

        for container in product_containers:
            try:
                # Extract product name from h2 tag
                name = None
                name_elem = container.find('h2')
                if name_elem:
                    name = name_elem.get_text(strip=True)

                # Extract price from span.priceNum
                # Try to get Happy price first (discounted price)
                price = None
                price_elem = container.find('div', class_='happyPrice')
                if price_elem:
                    # Found Happy price container, get the price number
                    price_span = price_elem.find('span', class_='priceNum')
                    if price_span:
                        price = price_span.get_text(strip=True)

                # Fallback to regular price if Happy price not found
                if not price:
                    price_elem = container.find('span', class_='priceNum')
                    if price_elem:
                        # Keep the exact price text as shown on the website
                        price = price_elem.get_text(strip=True)

                # Extract product URL from the anchor tag
                product_url = None
                link = container.find('a', href=True)
                if link:
                    product_url = self._make_absolute_url(link['href'])

                # Only add if we found at least name and price
                if name and price:
                    self.products.append({
                        'name': name,
                        'price': price,
                        'url': product_url or self.url
                    })

            except Exception as e:
                # Skip products that fail to parse
                print(f"Error parsing product: {e}")
                continue

    def parse_single_product(self):
        """
        Parse a single product page (if URL is for a single product)

        TODO: Implement if needed
        """
        pass
