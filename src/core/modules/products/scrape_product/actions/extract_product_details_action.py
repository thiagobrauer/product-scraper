"""Action to extract product details from a product page."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.scrape_product.gateways.ecommerce_gateway import (
    EcommerceGateway,
)
from src.core.modules.products.scrape_product.entities.product import Product


class ExtractProductDetailsAction:
    """Extract all product details from the current product page."""

    def __init__(self, ecommerce_gateway: EcommerceGateway, log: LogInterface):
        self.ecommerce = ecommerce_gateway
        self.log = log

    def apply(self) -> Product:
        """
        Extract all available product details from the current page.

        Returns:
            A Product entity with all extracted details
        """
        self.log.info("Extracting product details")
        product = self.ecommerce.extract_product_details()
        self.log.info(
            "Product details extracted",
            {"name": product.name, "sku": product.sku},
        )
        return product
