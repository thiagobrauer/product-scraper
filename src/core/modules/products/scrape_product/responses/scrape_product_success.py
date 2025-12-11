"""Success response for scrape product use case."""
from dataclasses import dataclass

from src.core.modules.products.scrape_product.entities.product import Product
from src.core.modules.products.scrape_product.responses.scrape_product_response import (
    ScrapeProductResponse,
)


@dataclass(frozen=True)
class ScrapeProductSuccess(ScrapeProductResponse):
    """Success response containing the scraped product."""

    product: Product
