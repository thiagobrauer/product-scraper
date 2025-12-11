"""
E-commerce Web Scraper with AI Enrichment

This script scrapes product data from e-commerce websites and enriches
the extracted data using AI.
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Optional, List

from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Product:
    """Represents a scraped product."""
    name: str
    price: Optional[str] = None
    original_price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    images: Optional[List[str]] = None
    url: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    sizes: Optional[List[str]] = None
    material: Optional[str] = None
    specifications: Optional[dict] = None
    enriched_data: Optional[dict] = None


class RiachueloScraper:
    """Scrapes product data from Riachuelo website using Playwright."""

    BASE_URL = "https://www.riachuelo.com.br"
    SEARCH_URL = f"{BASE_URL}/busca"

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start(self):
        """Start the browser."""
        self.playwright = sync_playwright().start()

        # Use Firefox as it's generally better at avoiding detection
        self.browser = self.playwright.firefox.launch(headless=self.headless)

        # Create a context with realistic settings
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )
        self.page = self.context.new_page()

    def close(self):
        """Close the browser."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def search_and_get_product(self, query: str) -> Optional[Product]:
        """
        Search for a product on Riachuelo and navigate to the first result
        to extract detailed product information.

        Args:
            query: The search term (e.g., product code like "15247848")

        Returns:
            Product object with detailed information, or None if not found
        """
        # First, go to the homepage to establish a session
        print(f"Navigating to homepage: {self.BASE_URL}")
        self.page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)

        # Wait for the page to load
        print("Waiting for homepage to load...")
        self.page.wait_for_timeout(3000)

        # Navigate directly to search URL (more reliable)
        print(f"Searching for: {query}")
        search_url = f"{self.SEARCH_URL}?q={query}"
        self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

        # Wait for navigation/results
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            print("Network idle timeout, continuing anyway...")

        # Give extra time for dynamic content
        self.page.wait_for_timeout(3000)

        print(f"Search results URL: {self.page.url}")

        # Find the first product link and click it
        product_link = self._get_first_product_link()
        if not product_link:
            print("No products found in search results")
            return None

        # Navigate to the product page
        print(f"Navigating to product page: {product_link}")
        self.page.goto(product_link, wait_until="domcontentloaded", timeout=60000)

        # Wait for the product page to load
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            print("Network idle timeout, continuing anyway...")

        self.page.wait_for_timeout(3000)

        print(f"Product page URL: {self.page.url}")

        # Scroll down to load any lazy-loaded content
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)

        # Try to expand product info sections if they exist
        try:
            # Look for expandable sections with product info
            expand_buttons = self.page.query_selector_all("[aria-expanded='false'], button[class*='expand'], button[class*='accordion']")
            for btn in expand_buttons[:3]:  # Limit to first 3 to avoid clicking too many
                try:
                    btn.click()
                    self.page.wait_for_timeout(500)
                except Exception:
                    pass
        except Exception:
            pass

        # Save screenshot for debugging
        self.page.screenshot(path="product_page.png")
        print("Screenshot saved to product_page.png")

        # Save HTML for debugging
        html_content = self.page.content()
        with open("product_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("HTML saved to product_page.html")

        # Extract detailed product information
        product = self._extract_product_details()

        return product

    def _get_first_product_link(self) -> Optional[str]:
        """Get the URL of the first product in search results."""
        # Try to find product links
        product_selectors = [
            "#showcase ol > li a[href]",
            "[data-testid='open-product-recommendation']",
            "a[href*='riachuelo']",
        ]

        for selector in product_selectors:
            link = self.page.query_selector(selector)
            if link:
                href = link.get_attribute("href")
                if href:
                    url = href if href.startswith("http") else f"{self.BASE_URL}{href}"
                    print(f"Found product link: {url}")
                    return url

        return None

    def _extract_product_details(self) -> Product:
        """Extract detailed product information from the product page."""
        import re

        # First, try to extract structured data from JSON-LD
        json_ld_data = self._extract_json_ld()

        # Extract product name
        name = None
        if json_ld_data:
            name = json_ld_data.get("name")
        if not name:
            name_selectors = ["h1", "[data-testid='product-name']", "[class*='ProductName']"]
            for selector in name_selectors:
                elem = self.page.query_selector(selector)
                if elem:
                    name = elem.inner_text().strip()
                    if name:
                        break

        # Extract current price from JSON-LD or page
        price = None
        if json_ld_data:
            # First try direct offers (for Product type)
            if "offers" in json_ld_data:
                offers = json_ld_data["offers"]
                if isinstance(offers, dict):
                    price_value = offers.get("price") or offers.get("lowPrice")
                    if price_value:
                        price = f"R${price_value}"
                elif isinstance(offers, list) and offers:
                    price_value = offers[0].get("price")
                    if price_value:
                        price = f"R${price_value}"
            # For ProductGroup, get price from first variant
            if not price and "hasVariant" in json_ld_data:
                variants = json_ld_data["hasVariant"]
                if isinstance(variants, list) and variants:
                    first_variant = variants[0]
                    if "offers" in first_variant:
                        offers = first_variant["offers"]
                        if isinstance(offers, dict):
                            price_value = offers.get("price")
                            if price_value:
                                price = f"R${price_value}"

        # Extract original price (listPrice from JSON-LD)
        original_price = None
        if json_ld_data and "offers" in json_ld_data:
            offers = json_ld_data["offers"]
            if isinstance(offers, dict):
                list_price = offers.get("highPrice")
                if list_price and str(list_price) != str(offers.get("lowPrice", "")):
                    original_price = f"R${list_price}"

        # Extract SKU
        sku = None
        if json_ld_data:
            sku = json_ld_data.get("sku")
        if not sku:
            current_url = self.page.url
            if "_" in current_url:
                sku_match = re.search(r'-(\d{8})_', current_url)
                if sku_match:
                    sku = sku_match.group(1)

        # Extract brand
        brand = None
        if json_ld_data and "brand" in json_ld_data:
            brand_data = json_ld_data["brand"]
            if isinstance(brand_data, dict):
                brand = brand_data.get("name")
            elif isinstance(brand_data, str):
                brand = brand_data

        # Extract description from JSON-LD
        description = None
        if json_ld_data:
            desc = json_ld_data.get("description", "")
            # Clean HTML tags from description
            description = re.sub(r'<[^>]+>', ' ', desc)
            description = re.sub(r'&nbsp;', ' ', description)
            description = re.sub(r'\s+', ' ', description).strip()

        # Extract all images
        images = []
        if json_ld_data and "image" in json_ld_data:
            img_data = json_ld_data["image"]
            if isinstance(img_data, list):
                images = img_data
            elif isinstance(img_data, str):
                images = [img_data]

        # Fallback: get images from page
        if not images:
            all_imgs = self.page.query_selector_all("img[src*='static.riachuelo']")
            for img in all_imgs:
                src = img.get_attribute("src")
                if src and src not in images and "portrait" in src:
                    images.append(src)

        # Extract available sizes from JSON-LD variants
        sizes = []
        if json_ld_data and "hasVariant" in json_ld_data:
            variants = json_ld_data["hasVariant"]
            if isinstance(variants, list):
                for variant in variants:
                    size = variant.get("size")
                    if size and size not in sizes:
                        sizes.append(size)
                # Sort sizes numerically if possible
                try:
                    sizes = sorted(sizes, key=lambda x: int(x))
                except ValueError:
                    sizes = sorted(sizes)

        # Extract color
        color = None
        if json_ld_data:
            color = json_ld_data.get("color")
        if not color and name and " - " in name:
            color = name.split(" - ")[-1].strip()

        # Extract category from JSON-LD or breadcrumbs
        category = None
        if json_ld_data and "category" in json_ld_data:
            category = json_ld_data["category"]
        if not category:
            # Try to extract from breadcrumbs
            breadcrumbs = self.page.query_selector_all("nav[aria-label='breadcrumb'] a")
            if breadcrumbs:
                category_parts = []
                for bc in breadcrumbs[1:]:  # Skip "Home"
                    text = bc.inner_text().strip()
                    if text:
                        category_parts.append(text)
                if category_parts:
                    category = " > ".join(category_parts)

        # Extract material from description
        material = None
        if description:
            # Look for composition pattern like "Poliéster 90%; Elastano 10%"
            # Match pattern: Material percentage; Material percentage (can have multiple)
            material_match = re.search(r'([A-Za-záéíóúãõâêîôûç\s]+\d+%(?:;\s*[A-Za-záéíóúãõâêîôûç\s]+\d+%)*)', description)
            if material_match:
                material = material_match.group(1).strip()

        # Build specifications from various sources
        specifications = {}
        if json_ld_data:
            if "gtin13" in json_ld_data:
                specifications["GTIN"] = json_ld_data["gtin13"]
            if "mpn" in json_ld_data:
                specifications["MPN"] = json_ld_data["mpn"]

        # Extract specifications from product-info-header table
        info_header = self.page.query_selector("#product-info-header")
        if info_header:
            # Look for table rows or key-value pairs
            rows = info_header.query_selector_all("tr")
            for row in rows:
                cells = row.query_selector_all("td, th")
                if len(cells) >= 2:
                    key = cells[0].inner_text().strip().rstrip(":")
                    value = cells[1].inner_text().strip()
                    if key and value:
                        specifications[key] = value
            # Also try looking for dl/dt/dd pattern
            if not rows:
                dts = info_header.query_selector_all("dt")
                dds = info_header.query_selector_all("dd")
                for dt, dd in zip(dts, dds):
                    key = dt.inner_text().strip().rstrip(":")
                    value = dd.inner_text().strip()
                    if key and value:
                        specifications[key] = value

        return Product(
            name=name or "Unknown Product",
            price=price,
            original_price=original_price,
            description=description,
            image_url=images[0] if images else None,
            images=images if images else None,
            url=self.page.url,
            sku=sku,
            brand=brand,
            category=category,
            color=color,
            sizes=sizes if sizes else None,
            material=material,
            specifications=specifications if specifications else None,
        )

    def _extract_json_ld(self) -> Optional[dict]:
        """Extract JSON-LD structured data from the page."""
        try:
            # Find all JSON-LD script tags
            scripts = self.page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                content = script.inner_text()
                if content:
                    data = json.loads(content)
                    # Look for Product or ProductGroup type
                    if isinstance(data, dict):
                        dtype = data.get("@type")
                        if dtype in ["Product", "ProductGroup"]:
                            return data
                        # Check for @graph structure
                        if "@graph" in data:
                            for item in data["@graph"]:
                                if item.get("@type") in ["Product", "ProductGroup"]:
                                    return item
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("@type") in ["Product", "ProductGroup"]:
                                return item
        except Exception as e:
            print(f"Error extracting JSON-LD: {e}")
        return None

    def _extract_search_results(self) -> List[Product]:
        """Extract product information from search results page."""
        products = []

        # Riachuelo uses an ordered list with li items for product cards
        # The main container is #showcase with an ol inside
        product_selectors = [
            "#showcase ol > li",  # Main product listing
            "ol.MuiGrid-container > li",  # Alternative selector
            "[data-testid='open-product-recommendation']",  # Product links
        ]

        product_elements = []
        for selector in product_selectors:
            elements = self.page.query_selector_all(selector)
            if elements:
                print(f"Found {len(elements)} products with selector: {selector}")
                product_elements = elements
                break

        if not product_elements:
            print("No product elements found. Dumping page info...")
            print(f"Current URL: {self.page.url}")
            print(f"Page title: {self.page.title()}")

            body_html = self.page.inner_html("body")
            print(f"\nPage body length: {len(body_html)} characters")

        for element in product_elements:
            try:
                product = self._parse_product_card(element)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"Error parsing product card: {e}")

        return products

    def _parse_product_card(self, element) -> Optional[Product]:
        """Parse a single product card element from Riachuelo."""
        try:
            # Extract product SKU from the li id attribute
            sku = element.get_attribute("id")

            # Extract product name from h3 or aria-label
            name = None
            name_elem = element.query_selector("h3")
            if name_elem:
                name = name_elem.inner_text().strip()

            if not name:
                # Try to get from aria-label of the link
                link = element.query_selector("a[aria-label]")
                if link:
                    name = link.get_attribute("aria-label")

            # Extract price - Riachuelo uses h6 for price
            price = None
            price_elem = element.query_selector("h6")
            if price_elem:
                price = price_elem.inner_text().strip()

            # Extract URL from the main product link
            url = None
            link_elem = element.query_selector("a[href]")
            if link_elem:
                href = link_elem.get_attribute("href")
                if href:
                    url = href if href.startswith("http") else f"{self.BASE_URL}{href}"

            # Extract image URL
            image_url = None
            img_elem = element.query_selector("img")
            if img_elem:
                image_url = img_elem.get_attribute("src") or img_elem.get_attribute("data-src")

            return Product(
                name=name or "Unknown Product",
                price=price,
                url=url,
                image_url=image_url,
                sku=sku
            )
        except Exception as e:
            print(f"Error in _parse_product_card: {e}")
            return None


class AIEnricher:
    """Enriches product data using AI."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def enrich_product(self, product: Product) -> Product:
        """
        Enrich product data with AI-generated insights.
        Placeholder for AI integration.
        """
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not set. Skipping AI enrichment.")
            return product

        # TODO: Implement AI enrichment using OpenAI API
        product.enriched_data = {
            "status": "AI enrichment not yet implemented",
            "suggested_enrichments": [
                "category_classification",
                "description_summary",
                "keyword_extraction"
            ]
        }
        return product


def main():
    """Main entry point for the scraper."""
    print("Riachuelo E-commerce Scraper")
    print("=" * 40)

    # Search for product 15247848
    product_code = "15247848"

    print(f"\nSearching for product: {product_code}")

    with RiachueloScraper(headless=True) as scraper:
        product = scraper.search_and_get_product(product_code)

        if product:
            print("\n" + "=" * 40)
            print("PRODUCT DETAILS")
            print("=" * 40)
            print(json.dumps(asdict(product), indent=2, ensure_ascii=False))
        else:
            print("\nNo product found.")


if __name__ == "__main__":
    main()
