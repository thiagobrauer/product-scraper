"""Base response class for enrich product use case."""
from abc import ABC, abstractmethod


class EnrichProductResponse(ABC):
    """Abstract base class for enrichment responses."""

    @abstractmethod
    def is_success(self) -> bool:
        """Return True if enrichment was successful."""
        pass
