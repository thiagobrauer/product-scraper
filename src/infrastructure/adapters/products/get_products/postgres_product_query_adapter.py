"""PostgreSQL adapter for querying products with enrichments."""
from typing import Optional, List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.modules.products.get_products.entities.product_with_enrichment import (
    ProductWithEnrichment,
    EnrichedData,
    Attributes,
    Categorization,
    Content,
    EnrichmentMetadata,
    MaterialParsed,
    TargetAudience,
)


class PostgresProductQueryAdapter:
    """
    Adapter that implements ProductQueryGateway using PostgreSQL.

    Uses the products_with_enrichments view for efficient querying.
    """

    def __init__(self, database_url: str = None, engine: Engine = None):
        """
        Initialize the adapter.

        Args:
            database_url: PostgreSQL connection URL
            engine: Existing SQLAlchemy engine (for sharing connections)
        """
        if engine:
            self.engine = engine
        elif database_url:
            self.engine = create_engine(database_url)
        else:
            raise ValueError("Either database_url or engine must be provided")

    def find_all(self) -> List[ProductWithEnrichment]:
        """
        Retrieve all products with their enrichment data.

        Returns:
            List of products with enrichments
        """
        with self.engine.connect() as conn:
            query = text("""
                SELECT * FROM products_with_enrichments
                ORDER BY created_at DESC
            """)
            results = conn.execute(query).fetchall()
            return [self._row_to_entity(row) for row in results]

    def find_by_id(self, product_id: int) -> Optional[ProductWithEnrichment]:
        """
        Find a product by its ID with enrichment data.

        Args:
            product_id: The product ID

        Returns:
            The product if found, None otherwise
        """
        with self.engine.connect() as conn:
            query = text("""
                SELECT * FROM products_with_enrichments
                WHERE id = :id
            """)
            result = conn.execute(query, {"id": product_id}).fetchone()

            if result is None:
                return None

            return self._row_to_entity(result)

    def _row_to_entity(self, row) -> ProductWithEnrichment:
        """Convert a database row to ProductWithEnrichment entity."""
        # Build enriched_data if enrichment exists
        enriched_data = None
        if row.enrichment_id is not None:
            # Build material parsed
            material_parsed = None
            if row.material_parsed:
                material_parsed = MaterialParsed(
                    primary=row.material_parsed.get("primary"),
                    secondary=row.material_parsed.get("secondary"),
                    percentage=row.material_parsed.get("percentage"),
                )

            # Build target audience
            target_audience = None
            if row.target_gender or row.target_age_group:
                target_audience = TargetAudience(
                    gender=row.target_gender,
                    age_group=row.target_age_group,
                    age_range=row.target_age_range,
                )

            # Build attributes
            attributes = Attributes(
                sleeve_type=row.sleeve_type,
                neckline=row.neckline,
                fit=row.fit,
                closure_type=row.closure_type,
                pattern=row.pattern,
                heel_height=getattr(row, 'heel_height', None),
                toe_style=getattr(row, 'toe_style', None),
                uv_protection=row.uv_protection,
                material_parsed=material_parsed,
                care_instructions=row.care_instructions.split(", ") if row.care_instructions else None,
                key_features=row.key_features or [],
            )

            # Build categorization
            categorization = Categorization(
                occasions=row.occasions or [],
                seasons=row.seasons or [],
                style_tags=row.style_tags or [],
                target_audience=target_audience,
                search_keywords=row.search_keywords or [],
                complementary_categories=row.complementary_categories or [],
            )

            # Build content
            content = Content(
                seo_title=row.seo_title,
                meta_description=row.meta_description,
                short_description=row.short_description,
                marketing_highlights=row.marketing_highlights or [],
                image_alt_text=row.image_alt_text,
            )

            # Build metadata
            enrichment_metadata = EnrichmentMetadata(
                model=row.enrichment_model,
                enriched_at=row.enriched_at,
                version=row.enrichment_version,
            )

            enriched_data = EnrichedData(
                attributes=attributes,
                categorization=categorization,
                content=content,
                enrichment_metadata=enrichment_metadata,
            )

        return ProductWithEnrichment(
            id=row.id,
            sku=row.sku,
            name=row.name,
            price=row.price,
            original_price=row.original_price,
            description=row.description,
            image_url=row.image_url,
            images=row.images or [],
            url=row.url,
            brand=row.brand,
            category=row.category,
            color=row.color,
            sizes=row.sizes or [],
            material=row.material,
            specifications=row.specifications,
            enriched_data=enriched_data,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
