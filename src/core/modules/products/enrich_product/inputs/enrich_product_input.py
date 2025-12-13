"""Input data for the enrich product use case."""
from typing import Dict, Any, Optional


class EnrichProductInput:
    """Input containing product data to be enriched."""

    def __init__(
        self,
        product_data: Dict[str, Any],
        product_id: Optional[int] = None,
    ):
        """
        Initialize enrichment input.

        Args:
            product_data: Dictionary containing product information
            product_id: Optional database ID if product is already saved
        """
        self._product_data = product_data
        self._product_id = product_id

    @property
    def product_data(self) -> Dict[str, Any]:
        """Return the product data to be enriched."""
        return self._product_data

    @property
    def product_id(self) -> Optional[int]:
        """Return the product database ID if available."""
        return self._product_id
