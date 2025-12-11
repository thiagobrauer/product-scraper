"""Use case for scraping product information from e-commerce website."""
from typing import Optional

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.scrape_product.gateways.ecommerce_gateway import (
    EcommerceGateway,
)
from src.core.modules.products.scrape_product.gateways.product_repository_gateway import (
    ProductRepositoryGateway,
)
from src.core.modules.products.scrape_product.inputs.scrape_product_input import (
    ScrapeProductInput,
)
from src.core.modules.products.scrape_product.responses.scrape_product_response import (
    ScrapeProductResponse,
)
from src.core.modules.products.scrape_product.responses.scrape_product_success import (
    ScrapeProductSuccess,
)
from src.core.modules.products.scrape_product.responses.scrape_product_error import (
    ScrapeProductError,
)
from src.core.modules.products.scrape_product.actions.navigate_to_search_action import (
    NavigateToSearchAction,
)
from src.core.modules.products.scrape_product.actions.find_product_link_action import (
    FindProductLinkAction,
)
from src.core.modules.products.scrape_product.actions.navigate_to_product_action import (
    NavigateToProductAction,
)
from src.core.modules.products.scrape_product.actions.extract_product_details_action import (
    ExtractProductDetailsAction,
)
from src.core.modules.products.scrape_product.exceptions.product_not_found_exception import (
    ProductNotFoundException,
)
from src.core.modules.products.scrape_product.exceptions.navigation_exception import (
    NavigationException,
)


class ScrapeProductUseCase:
    """
    Use case for scraping product details from an e-commerce website.

    This use case is platform-agnostic and orchestrates the following actions:
    1. Navigate to the search page with the given query
    2. Find the first product link in search results
    3. Navigate to the product page
    4. Extract all product details
    5. Save product to repository (if provided)

    The platform-specific logic is delegated to the EcommerceGateway,
    allowing this use case to work with any e-commerce platform.
    """

    def __init__(
        self,
        ecommerce_gateway: EcommerceGateway,
        log: LogInterface,
        product_repository: Optional[ProductRepositoryGateway] = None,
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            ecommerce_gateway: Platform-specific adapter for e-commerce operations
            log: Logger for tracking progress
            product_repository: Optional repository for persisting products
        """
        self.ecommerce = ecommerce_gateway
        self.log = log
        self.product_repository = product_repository

        # Initialize actions with the ecommerce gateway and logger
        self.navigate_to_search = NavigateToSearchAction(ecommerce_gateway, log)
        self.find_product_link = FindProductLinkAction(ecommerce_gateway, log)
        self.navigate_to_product = NavigateToProductAction(ecommerce_gateway, log)
        self.extract_product_details = ExtractProductDetailsAction(ecommerce_gateway, log)

    def apply(self, input_data: ScrapeProductInput) -> ScrapeProductResponse:
        """
        Execute the product scraping use case.

        Args:
            input_data: Input containing the search query and configuration

        Returns:
            ScrapeProductSuccess with the product data on success,
            ScrapeProductError with error details on failure
        """
        try:
            self.log.info(
                "Starting product scrape",
                {
                    "platform": self.ecommerce.platform_name,
                    "query": input_data.query,
                },
            )

            # Step 1: Navigate to search page
            self.navigate_to_search.apply(input_data.query)

            # Step 2: Find product link in search results
            product_link = self.find_product_link.apply(input_data.query)

            # Step 3: Navigate to product page
            self.navigate_to_product.apply(
                product_link, save_debug_files=input_data.save_debug_files
            )

            # Step 4: Extract product details
            product = self.extract_product_details.apply()

            # Step 5: Save to repository if available
            if self.product_repository:
                self.log.info("Saving product to database", {"sku": product.sku})
                self.product_repository.save(product)
                self.log.info("Product saved successfully")

            self.log.info(
                "Product scrape completed successfully",
                {"product_name": product.name, "sku": product.sku},
            )

            return ScrapeProductSuccess(product=product)

        except ProductNotFoundException as e:
            self.log.error("Product not found", {"query": e.query})
            return ScrapeProductError(
                error_type="product_not_found",
                message=str(e),
                query=input_data.query,
            )

        except NavigationException as e:
            self.log.error("Navigation failed", {"url": e.url, "reason": e.reason})
            return ScrapeProductError(
                error_type="navigation_error",
                message=str(e),
                query=input_data.query,
            )

        except Exception as e:
            self.log.error("Unexpected error during scrape", {"error": str(e)})
            return ScrapeProductError(
                error_type="unexpected_error",
                message=str(e),
                query=input_data.query,
            )
