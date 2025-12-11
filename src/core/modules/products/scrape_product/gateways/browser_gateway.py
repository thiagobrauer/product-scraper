"""Browser gateway protocol for web scraping operations."""
from typing import Protocol, Optional, List, Dict, Any


class BrowserGateway(Protocol):
    """Protocol defining browser operations for web scraping."""

    def navigate_to(self, url: str) -> None:
        """Navigate to a URL."""
        ...

    def get_current_url(self) -> str:
        """Get the current page URL."""
        ...

    def wait_for_page_load(self, timeout: int = 15000) -> None:
        """Wait for the page to fully load."""
        ...

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page."""
        ...

    def get_page_html(self) -> str:
        """Get the full HTML content of the page."""
        ...

    def save_screenshot(self, path: str) -> None:
        """Save a screenshot of the current page."""
        ...

    def query_selector(self, selector: str) -> Optional[Any]:
        """Find a single element by CSS selector."""
        ...

    def query_selector_all(self, selector: str) -> List[Any]:
        """Find all elements matching a CSS selector."""
        ...

    def get_element_text(self, element: Any) -> str:
        """Get the text content of an element."""
        ...

    def get_element_attribute(self, element: Any, attribute: str) -> Optional[str]:
        """Get an attribute value from an element."""
        ...

    def click_element(self, element: Any) -> None:
        """Click on an element."""
        ...

    def extract_json_ld(self) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD structured data from the page."""
        ...
