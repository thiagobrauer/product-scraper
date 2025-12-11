"""Action to navigate to a product page."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.scrape_product.gateways.ecommerce_gateway import (
    EcommerceGateway,
)


class NavigateToProductAction:
    """Navigate to a product detail page and prepare it for scraping."""

    def __init__(self, ecommerce_gateway: EcommerceGateway, log: LogInterface):
        self.ecommerce = ecommerce_gateway
        self.log = log

    def apply(self, product_url: str, save_debug_files: bool = False) -> None:
        """
        Navigate to the product page and prepare content for extraction.

        Args:
            product_url: The URL of the product page
            save_debug_files: Whether to save debug files (screenshot, HTML)
        """
        self.log.info("Navigating to product page", {"url": product_url})
        self.ecommerce.navigate_to_product(product_url, save_debug_files)
        self.log.info("Product page loaded")
