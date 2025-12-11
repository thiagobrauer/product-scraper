"""Playwright implementation of the BrowserGateway protocol."""
import json
from typing import Optional, List, Dict, Any

from playwright.sync_api import Page, ElementHandle


class PlaywrightBrowserAdapter:
    """
    Adapter that implements BrowserGateway using Playwright.

    This adapter wraps a Playwright Page object and provides
    the browser operations needed by the scraping actions.
    """

    def __init__(self, page: Page):
        """
        Initialize the adapter with a Playwright page.

        Args:
            page: The Playwright Page object to use for browser operations
        """
        self.page = page

    def navigate_to(self, url: str) -> None:
        """Navigate to the specified URL."""
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url

    def wait_for_page_load(self, timeout: int = 15000) -> None:
        """Wait for the page to finish loading (best effort)."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception:
            # Network idle timeout is acceptable, continue anyway
            pass
        # Additional wait for dynamic content
        self.page.wait_for_timeout(3000)

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the page to load dynamic content."""
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1000)

    def get_page_html(self) -> str:
        """Get the full HTML content of the page."""
        return self.page.content()

    def save_screenshot(self, path: str) -> None:
        """Save a screenshot of the current page."""
        self.page.screenshot(path=path, full_page=True)

    def query_selector(self, selector: str) -> Optional[ElementHandle]:
        """Find a single element matching the selector."""
        return self.page.query_selector(selector)

    def query_selector_all(self, selector: str) -> List[ElementHandle]:
        """Find all elements matching the selector."""
        return self.page.query_selector_all(selector)

    def get_element_text(self, element: ElementHandle) -> str:
        """Get the text content of an element."""
        return element.text_content() or ""

    def get_element_attribute(
        self, element: ElementHandle, attribute: str
    ) -> Optional[str]:
        """Get an attribute value from an element."""
        return element.get_attribute(attribute)

    def click_element(self, element: ElementHandle) -> None:
        """Click on an element."""
        element.click()

    def extract_json_ld(self) -> Optional[Dict[str, Any]]:
        """
        Extract JSON-LD structured data from the page.

        Returns:
            The parsed JSON-LD data or None if not found
        """
        scripts = self.page.query_selector_all('script[type="application/ld+json"]')

        for script in scripts:
            try:
                content = script.text_content()
                if content:
                    data = json.loads(content)
                    # Handle array of JSON-LD objects
                    if isinstance(data, list):
                        for item in data:
                            if item.get("@type") in ["Product", "ProductGroup"]:
                                return item
                    elif data.get("@type") in ["Product", "ProductGroup"]:
                        return data
            except json.JSONDecodeError:
                continue

        return None
