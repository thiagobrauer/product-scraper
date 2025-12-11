"""Input DTO for scrape product use case."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ScrapeProductInput:
    """Input data for scraping a product."""

    query: str  # Search query (e.g., product code "15247848")
    save_debug_files: bool = False  # Whether to save HTML/screenshots for debugging
