"""PostgreSQL implementation of the ProductRepositoryGateway protocol."""
import json
from typing import Optional, List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.modules.products.scrape_product.entities.product import Product


class PostgresProductRepositoryAdapter:
    """
    Adapter that implements ProductRepositoryGateway using PostgreSQL.

    Uses SQLAlchemy for database operations.
    """

    def __init__(self, database_url: str):
        """
        Initialize the adapter with a database connection.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.engine: Engine = create_engine(database_url)

    def save(self, product: Product) -> Product:
        """
        Save a product to the database (upsert by SKU).

        Args:
            product: The product to save

        Returns:
            The saved product
        """
        with self.engine.connect() as conn:
            # Use upsert (INSERT ... ON CONFLICT UPDATE)
            query = text("""
                INSERT INTO products (
                    sku, name, price, original_price, description,
                    image_url, images, url, brand, category,
                    color, sizes, material, specifications
                ) VALUES (
                    :sku, :name, :price, :original_price, :description,
                    :image_url, :images, :url, :brand, :category,
                    :color, :sizes, :material, :specifications
                )
                ON CONFLICT (sku) DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    original_price = EXCLUDED.original_price,
                    description = EXCLUDED.description,
                    image_url = EXCLUDED.image_url,
                    images = EXCLUDED.images,
                    url = EXCLUDED.url,
                    brand = EXCLUDED.brand,
                    category = EXCLUDED.category,
                    color = EXCLUDED.color,
                    sizes = EXCLUDED.sizes,
                    material = EXCLUDED.material,
                    specifications = EXCLUDED.specifications
                RETURNING id
            """)

            result = conn.execute(
                query,
                {
                    "sku": product.sku,
                    "name": product.name,
                    "price": product.price,
                    "original_price": product.original_price,
                    "description": product.description,
                    "image_url": product.image_url,
                    "images": json.dumps(product.images) if product.images else None,
                    "url": product.url,
                    "brand": product.brand,
                    "category": product.category,
                    "color": product.color,
                    "sizes": json.dumps(product.sizes) if product.sizes else None,
                    "material": product.material,
                    "specifications": (
                        json.dumps(product.specifications)
                        if product.specifications
                        else None
                    ),
                },
            )
            row = result.fetchone()
            if row:
                product.set_id(row[0])
            conn.commit()

        return product

    def find_by_sku(self, sku: str) -> Optional[Product]:
        """
        Find a product by its SKU.

        Args:
            sku: The product SKU

        Returns:
            The product if found, None otherwise
        """
        with self.engine.connect() as conn:
            query = text("SELECT * FROM products WHERE sku = :sku")
            result = conn.execute(query, {"sku": sku}).fetchone()

            if result is None:
                return None

            return self._row_to_product(result)

    def find_all(self) -> List[Product]:
        """
        Retrieve all products from the database.

        Returns:
            List of all products
        """
        with self.engine.connect() as conn:
            query = text("SELECT * FROM products ORDER BY created_at DESC")
            results = conn.execute(query).fetchall()

            return [self._row_to_product(row) for row in results]

    def _row_to_product(self, row) -> Product:
        """Convert a database row to a Product entity."""
        return Product(
            id=row.id,
            name=row.name,
            price=row.price,
            original_price=row.original_price,
            description=row.description,
            image_url=row.image_url,
            images=row.images if row.images else None,
            url=row.url,
            sku=row.sku,
            brand=row.brand,
            category=row.category,
            color=row.color,
            sizes=row.sizes if row.sizes else None,
            material=row.material,
            specifications=row.specifications if row.specifications else None,
        )
