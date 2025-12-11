"""Action to find the first product link in search results."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.scrape_product.gateways.ecommerce_gateway import (
    EcommerceGateway,
)


class FindProductLinkAction:
    """Find the first product link from search results."""

    def __init__(self, ecommerce_gateway: EcommerceGateway, log: LogInterface):
        self.ecommerce = ecommerce_gateway
        self.log = log

    def apply(self, query: str) -> str:
        """
        Find and return the URL of the first product in search results.

        Args:
            query: The search query (for error messages)

        Returns:
            The absolute URL of the first product

        Raises:
            ProductNotFoundException: If no product is found
        """
        self.log.info("Finding product link in search results")
        product_link = self.ecommerce.find_product_link(query)
        self.log.info("Found product link", {"link": product_link})
        return product_link
