"""Gateway protocol for e-commerce platform operations."""
from typing import Protocol

from src.core.modules.products.scrape_product.entities.product import Product


class EcommerceGateway(Protocol):
    """
    Protocol defining e-commerce platform-specific operations.

    Each e-commerce platform (Riachuelo, Amazon, etc.) should have
    its own adapter implementing this protocol. This allows the
    use case to be platform-agnostic.
    """

    @property
    def platform_name(self) -> str:
        """Return the name of the e-commerce platform."""
        ...

    def navigate_to_search(self, query: str) -> str:
        """
        Navigate to the search results page for the given query.

        Args:
            query: The search query (product code, name, etc.)

        Returns:
            The URL of the search results page
        """
        ...

    def find_product_link(self, query: str) -> str:
        """
        Find and return the URL of the first matching product.

        Args:
            query: The search query (for error messages)

        Returns:
            The absolute URL of the first product

        Raises:
            ProductNotFoundException: If no product is found
        """
        ...

    def navigate_to_product(self, product_url: str, save_debug_files: bool = False) -> None:
        """
        Navigate to a product page and wait for it to load.

        Args:
            product_url: The URL of the product page
            save_debug_files: Whether to save debug files (screenshot, HTML)
        """
        ...

    def extract_product_details(self) -> Product:
        """
        Extract all product details from the current product page.

        Returns:
            A Product entity with all extracted details
        """
        ...
