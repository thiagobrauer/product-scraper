"""Action to navigate to search results page."""
from src.core.modules.products.scrape_product.gateways.browser_gateway import (
    BrowserGateway,
)


class NavigateToSearchAction:
    """Navigate to the search results page for a given query."""

    def __init__(self, browser_gateway: BrowserGateway):
        self.browser_gateway = browser_gateway

    def apply(self, base_url: str, query: str) -> str:
        """
        Navigate to homepage first, then to search URL.

        Args:
            base_url: The base URL of the website
            query: The search query

        Returns:
            The search results page URL
        """
        # Navigate to homepage to establish session
        self.browser_gateway.navigate_to(base_url)
        self.browser_gateway.wait_for_page_load()

        # Navigate to search URL
        search_url = f"{base_url}/busca?q={query}"
        self.browser_gateway.navigate_to(search_url)
        self.browser_gateway.wait_for_page_load()

        return self.browser_gateway.get_current_url()
