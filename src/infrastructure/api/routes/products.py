"""Products API routes."""
import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException

from src.infrastructure.api.controllers.products_controller import ProductsController
from src.infrastructure.adapters.products.get_products.postgres_product_query_adapter import (
    PostgresProductQueryAdapter,
)
from src.infrastructure.adapters.console_logger_adapter import ConsoleLoggerAdapter


router = APIRouter(prefix="/api/products", tags=["products"])


def get_controller() -> ProductsController:
    """Get the products controller instance."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(
            status_code=500,
            detail="Database not configured. Set DATABASE_URL environment variable."
        )

    # Create dependencies
    logger = ConsoleLoggerAdapter()
    product_query_gateway = PostgresProductQueryAdapter(database_url=database_url)

    return ProductsController(
        product_query_gateway=product_query_gateway,
        log=logger,
    )


@router.get("", response_model=List[Dict[str, Any]])
async def list_products():
    """
    List all products with their enrichment data.

    Returns a list of products ordered by creation date (newest first).
    """
    controller = get_controller()
    data, status_code = controller.list_products()

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data)

    return data


@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Get a specific product by ID.

    Args:
        product_id: The product ID

    Returns:
        The product with enrichment data

    Raises:
        404: If product is not found
    """
    controller = get_controller()
    data, status_code = controller.get_product(product_id)

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=data.get("message", "Error"))

    return data
