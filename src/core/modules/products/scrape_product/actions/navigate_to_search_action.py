"""Action to navigate to search results page."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.scrape_product.gateways.ecommerce_gateway import (
    EcommerceGateway,
)


class NavigateToSearchAction:
    """Navigate to the search results page for a given query."""

    def __init__(self, ecommerce_gateway: EcommerceGateway, log: LogInterface):
        self.ecommerce = ecommerce_gateway
        self.log = log

    def apply(self, query: str) -> str:
        """
        Navigate to the search results page.

        Args:
            query: The search query

        Returns:
            The search results page URL
        """
        self.log.info("Navigating to search page", {"query": query})
        url = self.ecommerce.navigate_to_search(query)
        self.log.info("Arrived at search page", {"url": url})
        return url
