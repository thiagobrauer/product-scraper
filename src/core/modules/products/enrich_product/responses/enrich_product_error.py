"""Error response for enrich product use case."""
from typing import Optional

from src.core.modules.products.enrich_product.responses.enrich_product_response import (
    EnrichProductResponse,
)


class EnrichProductError(EnrichProductResponse):
    """Response returned when product enrichment fails."""

    def __init__(
        self,
        error_type: str,
        message: str,
        step: Optional[str] = None,
    ):
        self._error_type = error_type
        self._message = message
        self._step = step

    @property
    def error_type(self) -> str:
        """Return the type of error."""
        return self._error_type

    @property
    def message(self) -> str:
        """Return the error message."""
        return self._message

    @property
    def step(self) -> Optional[str]:
        """Return the step where the error occurred."""
        return self._step

    def is_success(self) -> bool:
        return False
