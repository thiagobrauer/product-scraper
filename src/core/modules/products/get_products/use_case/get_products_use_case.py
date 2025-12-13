"""Use case for retrieving products."""
from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.get_products.gateways.product_query_gateway import (
    ProductQueryGateway,
)
from src.core.modules.products.get_products.responses.get_products_response import (
    GetProductsResponse,
    GetProductsSuccess,
    GetProductsError,
)


class GetProductsUseCase:
    """
    Use case for retrieving all products with their enrichment data.
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

    def apply(self) -> GetProductsResponse:
        """
        Execute the get products use case.

        Returns:
            GetProductsSuccess with the list of products on success,
            GetProductsError with error details on failure
        """
        try:
            self.log.info("Retrieving all products")

            products = self.product_query.find_all()

            self.log.info(
                "Products retrieved successfully",
                {"count": len(products)},
            )

            return GetProductsSuccess(products=products)

        except Exception as e:
            self.log.error("Error retrieving products", {"error": str(e)})
            return GetProductsError(
                error_type="database_error",
                message=str(e),
            )
