"""Gateway protocol for product enrichment repository operations."""
from typing import Protocol, Optional

from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductEnrichment,
)


class EnrichmentRepositoryGateway(Protocol):
    """
    Protocol defining repository operations for product enrichments.

    This allows the use case to be decoupled from the actual
    database implementation (PostgreSQL, MongoDB, etc.).
    """

    def save(self, enrichment: ProductEnrichment) -> ProductEnrichment:
        """
        Save a product enrichment to the repository.

        Args:
            enrichment: The enrichment data to save

        Returns:
            The saved enrichment (may include generated ID)
        """
        ...

    def find_by_product_id(self, product_id: int) -> Optional[ProductEnrichment]:
        """
        Find enrichment data for a specific product.

        Args:
            product_id: The ID of the product

        Returns:
            The enrichment if found, None otherwise
        """
        ...
