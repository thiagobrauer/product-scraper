"""Use case for retrieving a product by ID."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.get_products.gateways.product_query_gateway import (
    ProductQueryGateway,
)
from src.core.modules.products.get_products.responses.get_products_response import (
    GetProductsResponse,
    GetProductByIdSuccess,
    GetProductsError,
    ProductNotFoundError,
)


class GetProductByIdUseCase:
    """
    Use case for retrieving a single product by ID with its enrichment data.
    """

    def __init__(
        self,
        product_query_gateway: ProductQueryGateway,
        log: LogInterface,
    ):
        """
        Initialize the use case.

        Args:
            product_query_gateway: Gateway for querying products
            log: Logger for tracking progress
        """
        self.product_query = product_query_gateway
        self.log = log

    def apply(self, product_id: int) -> GetProductsResponse:
        """
        Execute the get product by ID use case.

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            GetProductByIdSuccess with the product on success,
            ProductNotFoundError if product doesn't exist,
            GetProductsError with error details on other failures
        """
        try:
            self.log.info("Retrieving product by ID", {"product_id": product_id})

            product = self.product_query.find_by_id(product_id)

            if product is None:
                self.log.info("Product not found", {"product_id": product_id})
                return ProductNotFoundError(product_id=product_id)

            self.log.info(
                "Product retrieved successfully",
                {"product_id": product_id, "name": product.name},
            )

            return GetProductByIdSuccess(product=product)

        except Exception as e:
            self.log.error(
                "Error retrieving product",
                {"product_id": product_id, "error": str(e)},
            )
            return GetProductsError(
                error_type="database_error",
                message=str(e),
            )
