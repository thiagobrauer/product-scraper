"""Gateway protocol for product persistence."""
from typing import Protocol, Optional, List

from src.core.modules.products.scrape_product.entities.product import Product


class ProductRepositoryGateway(Protocol):
    """Protocol for product repository operations."""

    def save(self, product: Product) -> Product:
        """
        Save a product to the repository.

        If a product with the same SKU exists, it will be updated.

        Args:
            product: The product to save

        Returns:
            The saved product with any generated fields (like ID)
        """
        ...

    def find_by_sku(self, sku: str) -> Optional[Product]:
        """
        Find a product by its SKU.

        Args:
            sku: The product SKU

        Returns:
            The product if found, None otherwise
        """
        ...

    def find_all(self) -> List[Product]:
        """
        Retrieve all products from the repository.

        Returns:
            List of all products
        """
        ...
