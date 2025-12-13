"""Controller for products API endpoints."""
from typing import List, Dict, Any, Tuple

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.get_products.use_case.get_products_use_case import (
    GetProductsUseCase,
)
from src.core.modules.products.get_products.use_case.get_product_by_id_use_case import (
    GetProductByIdUseCase,
)
from src.core.modules.products.get_products.gateways.product_query_gateway import (
    ProductQueryGateway,
)
from src.core.modules.products.get_products.responses.get_products_response import (
    GetProductsSuccess,
    GetProductByIdSuccess,
    ProductNotFoundError,
)


class ProductsController:
    """
    Controller that handles product API requests.

    Orchestrates use cases and transforms responses for the API layer.
    """

    def __init__(
        self,
        product_query_gateway: ProductQueryGateway,
        log: LogInterface,
    ):
        """
        Initialize the controller.

        Args:
            product_query_gateway: Gateway for querying products
            log: Logger for tracking operations
        """
        self.get_products_use_case = GetProductsUseCase(
            product_query_gateway=product_query_gateway,
            log=log,
        )
        self.get_product_by_id_use_case = GetProductByIdUseCase(
            product_query_gateway=product_query_gateway,
            log=log,
        )

    def list_products(self) -> Tuple[List[Dict[str, Any]], int]:
        """
        List all products with enrichment data.

        Returns:
            Tuple of (response data, HTTP status code)
        """
        response = self.get_products_use_case.apply()

        if isinstance(response, GetProductsSuccess):
            products_data = [product.to_dict() for product in response.products]
            return products_data, 200

        # Error case
        return {"error": response.error_type, "message": response.message}, 500

    def get_product(self, product_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Get a specific product by ID.

        Args:
            product_id: The product ID

        Returns:
            Tuple of (response data, HTTP status code)
        """
        response = self.get_product_by_id_use_case.apply(product_id)

        if isinstance(response, GetProductByIdSuccess):
            return response.product.to_dict(), 200

        if isinstance(response, ProductNotFoundError):
            return {"error": "not_found", "message": response.message}, 404

        # Other error case
        return {"error": response.error_type, "message": response.message}, 500
