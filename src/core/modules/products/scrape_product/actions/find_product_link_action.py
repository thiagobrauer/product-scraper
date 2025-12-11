"""Action to find the first product link in search results."""
from typing import Optional

from src.core.modules.products.scrape_product.gateways.browser_gateway import (
    BrowserGateway,
)
from src.core.modules.products.scrape_product.exceptions.product_not_found_exception import (
    ProductNotFoundException,
)


class FindProductLinkAction:
    """Find the first product link from search results."""

    PRODUCT_SELECTORS = [
        "#showcase ol > li a[href]",
        "[data-testid='open-product-recommendation']",
        "a[href*='riachuelo']",
    ]

    def __init__(self, browser_gateway: BrowserGateway):
        self.browser_gateway = browser_gateway

    def apply(self, base_url: str, query: str) -> str:
        """
        Find and return the URL of the first product in search results.

        Args:
            base_url: The base URL for building absolute URLs
            query: The search query (for error messages)

        Returns:
            The absolute URL of the first product

        Raises:
            ProductNotFoundException: If no product is found
        """
        for selector in self.PRODUCT_SELECTORS:
            element = self.browser_gateway.query_selector(selector)
            if element:
                href = self.browser_gateway.get_element_attribute(element, "href")
                if href:
                    # Convert to absolute URL if needed
                    url = href if href.startswith("http") else f"{base_url}{href}"
                    return url

        raise ProductNotFoundException(query)
