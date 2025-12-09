"""
Neptun-specific scraper
"""
from ..base import BaseScraper


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

    def _parse_price_to_int(self, price_text):
        """
        Parse price text and convert to integer (removing decimal separators)

        Examples:
        - "8.999" -> 8999
        - "1,234" -> 1234
        - "12.345" -> 12345
        """
        try:
            # Remove common currency symbols and whitespace
            cleaned = price_text.replace('ден', '').replace('MKD', '').strip()
            # Remove all decimal separators (comma and period)
            cleaned = cleaned.replace(',', '').replace('.', '')
            # Convert to integer
            return int(cleaned)
        except (ValueError, AttributeError):
            # Return None if parsing fails
            return None

    def parse_products(self):
        """
        Parse products from Neptun website

        Selectors based on Neptun's HTML structure:
        - Product container: div.theProduct
        - Product name: h2 (inside productCardBody)
        - Price: span.priceNum (inside discountPrice)
        - Product URL: a (direct child of theProduct)
        - Image: img tag inside the product container
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
                        price_text = price_span.get_text(strip=True)
                        # Convert to whole number (remove decimals)
                        price = self._parse_price_to_int(price_text)

                # Fallback to regular price if Happy price not found
                if not price:
                    price_elem = container.find('span', class_='priceNum')
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        # Convert to whole number (remove decimals)
                        price = self._parse_price_to_int(price_text)

                # Extract product URL from the anchor tag
                product_url = None
                link = container.find('a', href=True)
                if link:
                    product_url = self._make_absolute_url(link['href'])

                # Extract image URL from img tag
                image_url = None
                img = container.find('img')
                if img:
                    # Try to get src first, fallback to data-src for lazy loading
                    image_url = img.get('src') or img.get('data-src')
                    if image_url:
                        image_url = self._make_absolute_url(image_url)

                # Only add if we found at least name and price
                if name and price:
                    self.products.append({
                        'name': name,
                        'price': price,
                        'url': product_url or self.url,
                        'image': image_url
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
