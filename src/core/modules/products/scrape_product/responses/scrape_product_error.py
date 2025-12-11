"""Error response for scrape product use case."""
from dataclasses import dataclass
from typing import Optional

from src.core.modules.products.scrape_product.responses.scrape_product_response import (
    ScrapeProductResponse,
)


@dataclass(frozen=True)
class ScrapeProductError(ScrapeProductResponse):
    """Error response containing error details."""

    error_type: str
    message: str
    query: Optional[str] = None
