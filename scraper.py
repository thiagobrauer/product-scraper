# TODO: Add command-line arguments for product code and other options
# TODO: Implement more robust error handling and logging
# TODO: Extend to support multiple e-commerce sites
# TODO: Add unit and integration tests
# TODO: Consider asynchronous implementation for better performance
# TODO: Implement retry logic for network requests
# TODO: Add configuration management for different environments
# TODO: Integrate with a message queue for processing multiple products
# TODO: Implement caching for repeated product queries
# TODO: Add support for proxy rotation to avoid IP blocking
# TODO: Enhance data extraction to include more product details
# TODO: Implement rate limiting to avoid overwhelming the target site
# TODO: Add functionality to export scraped data to different formats (CSV, XML, etc.)
# TODO: Implement a scheduling mechanism for periodic scraping
# TODO: Add user authentication handling if required by the e-commerce site
# TODO: Consider using a headless browser farm for large-scale scraping
# TODO: Implement monitoring and alerting for scraper failures
# TODO: Add documentation for setup and usage instructions
# TODO: Explore machine learning techniques for better data extraction
# TODO: Implement a GUI for easier interaction with the scraper
# TODO: Add localization support for scraping from different regions
# TODO: Optimize performance for large-scale scraping tasks
# TODO: Ensure compliance with legal and ethical guidelines for web scraping
# TODO: Implement data validation and cleaning for scraped data
# TODO: Add support for scraping from mobile versions of e-commerce sites
# TODO: Consider using NoSQL databases for storing scraped data
# TODO: Force AI to return portuguese only in the JSON response

"""
E-commerce Web Scraper Orchestrator

This script orchestrates the product scraping use case using hexagonal architecture.
It wires together the infrastructure adapters and invokes the use case.

The scraper is platform-agnostic - to add support for a new e-commerce site,
create a new adapter implementing the EcommerceGateway protocol.
"""

import csv
import os
from typing import List, Optional

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
from src.core.modules.products.enrich_product.inputs.enrich_product_input import (
    EnrichProductInput,
)
from src.core.modules.products.enrich_product.use_case.enrich_product_use_case import (
    EnrichProductUseCase,
)
from src.core.modules.products.enrich_product.responses.enrich_product_success import (
    EnrichProductSuccess,
)
from src.infrastructure.adapters.products.scrape_product.playwright_browser_adapter import (
    PlaywrightBrowserAdapter,
)
from src.infrastructure.adapters.products.scrape_product.riachuelo_ecommerce_adapter import (
    RiachueloEcommerceAdapter,
)
from src.infrastructure.adapters.products.scrape_product.postgres_product_repository_adapter import (
    PostgresProductRepositoryAdapter,
)
from src.infrastructure.adapters.products.enrich_product.claude_ai_adapter import (
    ClaudeAIAdapter,
)
from src.infrastructure.adapters.products.enrich_product.postgres_enrichment_repository_adapter import (
    PostgresEnrichmentRepositoryAdapter,
)
from src.infrastructure.adapters.console_logger_adapter import ConsoleLoggerAdapter


SEARCH_TERMS_FILE = "search-terms.csv"


def load_search_terms(filepath: str = SEARCH_TERMS_FILE) -> List[str]:
    """Load search terms from CSV file."""
    terms = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            for row in reader:
                if row and row[0].strip():
                    terms.append(row[0].strip())
    except FileNotFoundError:
        print(f"Warning: {filepath} not found. No predefined search terms available.")
    return terms


def display_menu(search_terms: List[str]) -> List[str]:
    """Display interactive menu and return selected queries."""
    print("\n" + "=" * 50)
    print("AVAILABLE SEARCH TERMS")
    print("=" * 50)

    for i, term in enumerate(search_terms, 1):
        print(f"  {i:2}. {term}")

    print("\n" + "-" * 50)
    print("OPTIONS:")
    print("  a   - Scrape ALL products")
    print("  1-N - Scrape a specific product (enter the number)")
    print("  c   - Enter a CUSTOM search term")
    print("  q   - Quit")
    print("-" * 50)

    while True:
        choice = input("\nYour choice: ").strip().lower()

        if choice == "q":
            return []

        if choice == "a":
            return search_terms

        if choice == "c":
            custom_term = input("Enter custom search term: ").strip()
            if custom_term:
                return [custom_term]
            print("Invalid input. Please enter a search term.")
            continue

        # Try to parse as number or range
        try:
            # Check for range (e.g., "1-5")
            if "-" in choice:
                parts = choice.split("-")
                start = int(parts[0])
                end = int(parts[1])
                if 1 <= start <= len(search_terms) and 1 <= end <= len(search_terms):
                    return search_terms[start - 1 : end]
                print(f"Invalid range. Please enter numbers between 1 and {len(search_terms)}.")
                continue

            # Single number
            num = int(choice)
            if 1 <= num <= len(search_terms):
                return [search_terms[num - 1]]
            print(f"Invalid number. Please enter a number between 1 and {len(search_terms)}.")

        except ValueError:
            print("Invalid input. Please enter a number, 'a' for all, 'c' for custom, or 'q' to quit.")


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


def get_product_repository(logger):
    """Create product repository if database URL is configured."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        logger.info("Database configured, enabling persistence")
        return PostgresProductRepositoryAdapter(database_url)
    logger.info("No DATABASE_URL configured, running without persistence")
    return None


def get_enrichment_use_case(logger, product_repository) -> Optional[EnrichProductUseCase]:
    """Create enrichment use case if Claude API key is configured."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("No ANTHROPIC_API_KEY configured, skipping AI enrichment")
        return None

    logger.info("Claude API configured, enabling AI enrichment")

    # Create Claude AI adapter
    ai_adapter = ClaudeAIAdapter(api_key=api_key)

    # Create enrichment repository if database is available
    enrichment_repository = None
    if product_repository:
        enrichment_repository = PostgresEnrichmentRepositoryAdapter(
            engine=product_repository.engine
        )

    return EnrichProductUseCase(
        ai_gateway=ai_adapter,
        log=logger,
        enrichment_repository=enrichment_repository,
    )


def scrape_products(
    queries: List[str],
    scrape_use_case: ScrapeProductUseCase,
    enrich_use_case: Optional[EnrichProductUseCase] = None,
) -> dict:
    """
    Scrape multiple products and optionally enrich them with AI.

    Returns:
        Dictionary with 'success', 'failed', and 'enriched' lists
    """
    results = {"success": [], "failed": [], "enriched": []}

    total = len(queries)
    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 50}")
        print(f"SCRAPING {i}/{total}: {query}")
        print("=" * 50)

        input_data = ScrapeProductInput(
            query=query,
            save_debug_files=False,
        )

        response = scrape_use_case.apply(input_data)

        if isinstance(response, ScrapeProductSuccess):
            product = response.product
            results["success"].append({
                "query": query,
                "name": product.name,
                "sku": product.sku,
                "price": product.price,
            })
            print(f"\n✓ Scraped: {product.name}")
            print(f"  SKU: {product.sku} | Price: {product.price}")

            # Enrich product with AI if available
            if enrich_use_case:
                print(f"\n  Enriching with AI...")
                enrich_input = EnrichProductInput(
                    product_data=product.to_dict(),
                    product_id=product.id,  # Pass DB ID for saving enrichment
                )
                enrich_response = enrich_use_case.apply(enrich_input)

                if isinstance(enrich_response, EnrichProductSuccess):
                    enrichment = enrich_response.enrichment
                    results["enriched"].append(query)
                    print(f"  ✓ Enriched successfully")
                    print(f"    SEO Title: {enrichment.content.seo_title}")
                    print(f"    Keywords: {', '.join(enrichment.categorization.search_keywords[:3])}...")
                else:
                    print(f"  ✗ Enrichment failed: {enrich_response.message}")
        else:
            results["failed"].append({
                "query": query,
                "error": response.error_type,
                "message": response.message,
            })
            print(f"\n✗ Failed: {response.error_type}")
            print(f"  {response.message}")

    return results


def print_summary(results: dict):
    """Print a summary of scraping results."""
    print("\n" + "=" * 50)
    print("SCRAPING SUMMARY")
    print("=" * 50)

    success_count = len(results["success"])
    failed_count = len(results["failed"])
    enriched_count = len(results.get("enriched", []))
    total = success_count + failed_count

    print(f"\nTotal: {total} | Scraped: {success_count} | Failed: {failed_count} | Enriched: {enriched_count}")

    if results["success"]:
        print("\n✓ SCRAPED:")
        for item in results["success"]:
            enriched_marker = " [AI]" if item["query"] in results.get("enriched", []) else ""
            print(f"  - {item['query']}: {item['name']} ({item['price']}){enriched_marker}")

    if results["failed"]:
        print("\n✗ FAILED:")
        for item in results["failed"]:
            print(f"  - {item['query']}: {item['error']}")


def main():
    """Main entry point for the scraper."""
    print("=" * 50)
    print("E-COMMERCE PRODUCT SCRAPER")
    print("=" * 50)

    # Load search terms from CSV
    search_terms = load_search_terms()

    if not search_terms:
        print("\nNo search terms found. Please add terms to search-terms.csv")
        print("or enter a custom search term.")
        custom = input("\nEnter a search term (or 'q' to quit): ").strip()
        if not custom or custom.lower() == "q":
            print("Goodbye!")
            return
        queries = [custom]
    else:
        queries = display_menu(search_terms)

    if not queries:
        print("\nNo queries selected. Goodbye!")
        return

    print(f"\nWill scrape {len(queries)} product(s)")

    # Create infrastructure dependencies
    logger = ConsoleLoggerAdapter()
    product_repository = get_product_repository(logger)
    enrich_use_case = get_enrichment_use_case(logger, product_repository)

    with sync_playwright() as playwright:
        browser, context = create_browser_context(playwright)
        page = context.new_page()

        try:
            # Create browser adapter
            browser_adapter = PlaywrightBrowserAdapter(page)

            # Create platform-specific e-commerce adapter
            ecommerce_adapter = RiachueloEcommerceAdapter(browser_adapter)

            # Create scrape use case
            scrape_use_case = ScrapeProductUseCase(
                ecommerce_gateway=ecommerce_adapter,
                log=logger,
                product_repository=product_repository,
            )

            # Scrape all selected products (with optional enrichment)
            results = scrape_products(queries, scrape_use_case, enrich_use_case)

            # Print summary
            print_summary(results)

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
