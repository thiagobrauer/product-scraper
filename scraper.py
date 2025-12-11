"""
E-commerce Web Scraper Orchestrator

This script orchestrates the product scraping use case using hexagonal architecture.
It wires together the infrastructure adapters and invokes the use case.
"""

import json

from playwright.sync_api import sync_playwright

from src.core.modules.products.scrape_product.inputs.scrape_product_input import (
    ScrapeProductInput,
)
from src.core.modules.products.scrape_product.use_case.scrape_product_use_case import (
    ScrapeProductUseCase,
)
from src.core.modules.products.scrape_product.responses.scrape_product_success import (
    ScrapeProductSuccess,
)
from src.infrastructure.adapters.products.scrape_product.playwright_browser_adapter import (
    PlaywrightBrowserAdapter,
)
from src.infrastructure.adapters.console_logger_adapter import ConsoleLoggerAdapter


def create_browser_context(playwright):
    """Create a browser context with realistic settings."""
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        locale="pt-BR",
        timezone_id="America/Sao_Paulo",
    )
    return browser, context


def main():
    """Main entry point for the scraper."""
    print("Riachuelo E-commerce Scraper")
    print("=" * 40)

    product_code = "15247848"
    print(f"\nSearching for product: {product_code}")

    # Create infrastructure dependencies
    logger = ConsoleLoggerAdapter()

    with sync_playwright() as playwright:
        browser, context = create_browser_context(playwright)
        page = context.new_page()

        try:
            # Create adapters
            browser_adapter = PlaywrightBrowserAdapter(page)

            # Create and execute use case
            use_case = ScrapeProductUseCase(
                browser_gateway=browser_adapter,
                log=logger,
            )

            input_data = ScrapeProductInput(
                query=product_code,
                save_debug_files=True,
            )

            response = use_case.apply(input_data)

            # Handle response
            if isinstance(response, ScrapeProductSuccess):
                print("\n" + "=" * 40)
                print("PRODUCT DETAILS")
                print("=" * 40)
                print(json.dumps(response.product.to_dict(), indent=2, ensure_ascii=False))
            else:
                print(f"\nError: {response.error_type}")
                print(f"Message: {response.message}")

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
