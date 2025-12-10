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
    url: Optional[str] = None
    sku: Optional[str] = None
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

    def search_product(self, query: str) -> List[Product]:
        """
        Search for a product on Riachuelo by navigating to the homepage
        and using the search field.

        Args:
            query: The search term (e.g., product code like "15247848")

        Returns:
            List of Product objects found in search results
        """
        # First, go to the homepage to establish a session
        print(f"Navigating to homepage: {self.BASE_URL}")
        self.page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)

        # Wait for the page to load
        print("Waiting for homepage to load...")
        self.page.wait_for_timeout(3000)

        # Find and click the search input
        print("Looking for search field...")
        search_selectors = [
            "input[type='search']",
            "input[placeholder*='busca']",
            "input[placeholder*='Busca']",
            "input[name='q']",
            "[data-testid='search-input']",
            "input[class*='search']",
            "input[class*='Search']",
        ]

        search_input = None
        for selector in search_selectors:
            search_input = self.page.query_selector(selector)
            if search_input:
                print(f"Found search input with selector: {selector}")
                break

        if not search_input:
            # Try clicking on a search icon first
            print("Search input not found directly, looking for search button/icon...")
            search_buttons = [
                "button[aria-label*='search']",
                "button[aria-label*='busca']",
                "[data-testid='search-button']",
                "[class*='search'] button",
                "[class*='Search'] button",
                "svg[class*='search']",
            ]
            for selector in search_buttons:
                btn = self.page.query_selector(selector)
                if btn:
                    print(f"Found search button with selector: {selector}")
                    btn.click()
                    self.page.wait_for_timeout(1000)
                    # Now try to find the input again
                    for input_selector in search_selectors:
                        search_input = self.page.query_selector(input_selector)
                        if search_input:
                            break
                    break

        if search_input:
            print(f"Typing search query: {query}")
            search_input.click()
            search_input.fill(query)
            self.page.wait_for_timeout(500)

            # Press Enter to search
            search_input.press("Enter")
            print("Search submitted, waiting for results...")
        else:
            # Fallback: navigate directly to search URL
            print("Could not find search input, navigating directly to search URL...")
            search_url = f"{self.SEARCH_URL}?q={query}"
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

        # Wait for navigation/results
        try:
            self.page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            print("Network idle timeout, continuing anyway...")

        # Give extra time for dynamic content
        self.page.wait_for_timeout(3000)

        print(f"Current URL: {self.page.url}")

        # Save screenshot for debugging
        self.page.screenshot(path="search_results.png")
        print("Screenshot saved to search_results.png")

        # Save HTML for debugging
        html_content = self.page.content()
        with open("search_results.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("HTML saved to search_results.html")

        # Extract products from search results
        products = self._extract_search_results()

        return products

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
        products = scraper.search_product(product_code)

        print(f"\nFound {len(products)} product(s):")
        for i, product in enumerate(products, 1):
            print(f"\n--- Product {i} ---")
            print(json.dumps(asdict(product), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
