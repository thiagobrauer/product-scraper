"""Success response for enrich product use case."""
from src.core.modules.products.enrich_product.responses.enrich_product_response import (
    EnrichProductResponse,
)
from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductEnrichment,
)


class EnrichProductSuccess(EnrichProductResponse):
    """Response returned when product enrichment succeeds."""

    def __init__(self, enrichment: ProductEnrichment):
        self._enrichment = enrichment

    @property
    def enrichment(self) -> ProductEnrichment:
        """Return the enriched product data."""
        return self._enrichment

    def is_success(self) -> bool:
        return True
