"""Action to navigate to a product page."""
from src.core.modules.products.scrape_product.gateways.browser_gateway import (
    BrowserGateway,
)


class NavigateToProductAction:
    """Navigate to a product detail page and prepare it for scraping."""

    def __init__(self, browser_gateway: BrowserGateway):
        self.browser_gateway = browser_gateway

    def apply(self, product_url: str, save_debug_files: bool = False) -> str:
        """
        Navigate to the product page and prepare content for extraction.

        Args:
            product_url: The URL of the product page
            save_debug_files: Whether to save debug files (screenshot, HTML)

        Returns:
            The final product page URL
        """
        # Navigate to product page
        self.browser_gateway.navigate_to(product_url)
        self.browser_gateway.wait_for_page_load()

        # Scroll down to load lazy content
        self.browser_gateway.scroll_to_bottom()

        # Save debug files if requested
        if save_debug_files:
            self.browser_gateway.save_screenshot("product_page.png")
            html_content = self.browser_gateway.get_page_html()
            with open("product_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)

        return self.browser_gateway.get_current_url()
