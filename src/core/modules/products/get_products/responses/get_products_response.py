"""Response classes for get products use case."""
from typing import List, Optional
from abc import ABC, abstractmethod

from src.core.modules.products.get_products.entities.product_with_enrichment import (
    ProductWithEnrichment,
)


class GetProductsResponse(ABC):
    """Abstract base class for get products responses."""

    @abstractmethod
    def is_success(self) -> bool:
        """Return True if the operation was successful."""
        pass


class GetProductsSuccess(GetProductsResponse):
    """Response returned when products are retrieved successfully."""

    def __init__(self, products: List[ProductWithEnrichment]):
        self._products = products

    @property
    def products(self) -> List[ProductWithEnrichment]:
        """Return the list of products."""
        return self._products

    def is_success(self) -> bool:
        return True


class GetProductByIdSuccess(GetProductsResponse):
    """Response returned when a product is found."""

    def __init__(self, product: ProductWithEnrichment):
        self._product = product

    @property
    def product(self) -> ProductWithEnrichment:
        """Return the product."""
        return self._product

    def is_success(self) -> bool:
        return True


class GetProductsError(GetProductsResponse):
    """Response returned when an error occurs."""

    def __init__(self, error_type: str, message: str):
        self._error_type = error_type
        self._message = message

    @property
    def error_type(self) -> str:
        """Return the type of error."""
        return self._error_type

    @property
    def message(self) -> str:
        """Return the error message."""
        return self._message

    def is_success(self) -> bool:
        return False


class ProductNotFoundError(GetProductsResponse):
    """Response returned when a product is not found."""

    def __init__(self, product_id: int):
        self._product_id = product_id

    @property
    def product_id(self) -> int:
        """Return the product ID that was not found."""
        return self._product_id

    @property
    def message(self) -> str:
        """Return the error message."""
        return f"Product with ID {self._product_id} not found"

    def is_success(self) -> bool:
        return False
