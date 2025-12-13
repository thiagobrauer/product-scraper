"""Gateway protocol for querying products."""
from typing import Protocol, List, Optional

from src.core.modules.products.get_products.entities.product_with_enrichment import (
    ProductWithEnrichment,
)


class ProductQueryGateway(Protocol):
    """
    Protocol defining product query operations.

    This gateway is for read-only operations to retrieve
    products with their enrichment data.
    """

    def find_all(self) -> List[ProductWithEnrichment]:
        """
        Retrieve all products with their enrichment data.

        Returns:
            List of products with enrichments
        """
        ...

    def find_by_id(self, product_id: int) -> Optional[ProductWithEnrichment]:
        """
        Find a product by its ID with enrichment data.

        Args:
            product_id: The product ID

        Returns:
            The product if found, None otherwise
        """
        ...
