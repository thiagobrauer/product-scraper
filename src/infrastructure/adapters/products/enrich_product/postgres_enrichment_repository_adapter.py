"""PostgreSQL implementation of the EnrichmentRepositoryGateway protocol."""
import json
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductEnrichment,
    ProductAttributes,
    ProductCategorization,
    ProductContent,
    EnrichmentMetadata,
    MaterialParsed,
    TargetAudience,
)


class PostgresEnrichmentRepositoryAdapter:
    """
    Adapter that implements EnrichmentRepositoryGateway using PostgreSQL.

    Uses SQLAlchemy for database operations.
    """

    def __init__(self, database_url: str = None, engine: Engine = None):
        """
        Initialize the adapter with a database connection.

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

    def save(self, enrichment: ProductEnrichment) -> ProductEnrichment:
        """
        Save a product enrichment to the database.

        Args:
            enrichment: The enrichment data to save

        Returns:
            The saved enrichment
        """
        with self.engine.connect() as conn:
            query = text("""
                INSERT INTO product_enrichments (
                    product_id,
                    sleeve_type, neckline, fit, closure_type, pattern,
                    heel_height, toe_style, uv_protection,
                    material_parsed, care_instructions, key_features,
                    occasions, seasons, style_tags,
                    target_gender, target_age_group, target_age_range,
                    search_keywords, complementary_categories,
                    seo_title, meta_description, short_description,
                    marketing_highlights, image_alt_text,
                    model, version, enriched_at
                ) VALUES (
                    :product_id,
                    :sleeve_type, :neckline, :fit, :closure_type, :pattern,
                    :heel_height, :toe_style, :uv_protection,
                    :material_parsed, :care_instructions, :key_features,
                    :occasions, :seasons, :style_tags,
                    :target_gender, :target_age_group, :target_age_range,
                    :search_keywords, :complementary_categories,
                    :seo_title, :meta_description, :short_description,
                    :marketing_highlights, :image_alt_text,
                    :model, :version, :enriched_at
                )
                RETURNING id
            """)

            attrs = enrichment.attributes
            cat = enrichment.categorization
            content = enrichment.content
            meta = enrichment.metadata

            # Prepare target audience data
            target_audience = cat.target_audience

            result = conn.execute(
                query,
                {
                    "product_id": enrichment.product_id,
                    # Attributes
                    "sleeve_type": attrs.sleeve_type,
                    "neckline": attrs.neckline,
                    "fit": attrs.fit,
                    "closure_type": attrs.closure_type,
                    "pattern": attrs.pattern,
                    "heel_height": attrs.heel_height,
                    "toe_style": attrs.toe_style,
                    "uv_protection": attrs.uv_protection,
                    "material_parsed": (
                        json.dumps(attrs.material_parsed.to_dict())
                        if attrs.material_parsed
                        else None
                    ),
                    "care_instructions": (
                        ", ".join(attrs.care_instructions)
                        if attrs.care_instructions
                        else None
                    ),
                    "key_features": json.dumps(attrs.key_features),
                    # Categorization
                    "occasions": json.dumps(cat.occasions),
                    "seasons": json.dumps(cat.seasons),
                    "style_tags": json.dumps(cat.style_tags),
                    "target_gender": target_audience.gender if target_audience else None,
                    "target_age_group": target_audience.age_group if target_audience else None,
                    "target_age_range": target_audience.age_range if target_audience else None,
                    "search_keywords": json.dumps(cat.search_keywords),
                    "complementary_categories": json.dumps(cat.complementary_categories),
                    # Content
                    "seo_title": content.seo_title,
                    "meta_description": content.meta_description,
                    "short_description": content.short_description,
                    "marketing_highlights": json.dumps(content.marketing_highlights),
                    "image_alt_text": content.image_alt_text,
                    # Metadata
                    "model": meta.model if meta else None,
                    "version": meta.version if meta else "1.0",
                    "enriched_at": meta.enriched_at if meta else None,
                },
            )
            conn.commit()

        return enrichment

    def find_by_product_id(self, product_id: int) -> Optional[ProductEnrichment]:
        """
        Find the latest enrichment data for a specific product.

        Args:
            product_id: The ID of the product

        Returns:
            The enrichment if found, None otherwise
        """
        with self.engine.connect() as conn:
            query = text("""
                SELECT * FROM product_enrichments
                WHERE product_id = :product_id
                ORDER BY enriched_at DESC
                LIMIT 1
            """)
            result = conn.execute(query, {"product_id": product_id}).fetchone()

            if result is None:
                return None

            return self._row_to_enrichment(result)

    def _row_to_enrichment(self, row) -> ProductEnrichment:
        """Convert a database row to a ProductEnrichment entity."""
        # Parse material
        material_parsed = None
        if row.material_parsed:
            mp = row.material_parsed
            material_parsed = MaterialParsed(
                primary=mp.get("primary"),
                secondary=mp.get("secondary"),
                percentage=mp.get("percentage"),
            )

        # Parse care instructions
        care_instructions = None
        if row.care_instructions:
            care_instructions = [s.strip() for s in row.care_instructions.split(",")]

        # Build attributes
        attributes = ProductAttributes(
            sleeve_type=row.sleeve_type,
            neckline=row.neckline,
            fit=row.fit,
            closure_type=row.closure_type,
            pattern=row.pattern,
            heel_height=row.heel_height,
            toe_style=row.toe_style,
            uv_protection=row.uv_protection,
            material_parsed=material_parsed,
            care_instructions=care_instructions,
            key_features=row.key_features or [],
        )

        # Build target audience
        target_audience = None
        if row.target_gender or row.target_age_group:
            target_audience = TargetAudience(
                gender=row.target_gender,
                age_group=row.target_age_group,
                age_range=row.target_age_range,
            )

        # Build categorization
        categorization = ProductCategorization(
            occasions=row.occasions or [],
            seasons=row.seasons or [],
            style_tags=row.style_tags or [],
            target_audience=target_audience,
            search_keywords=row.search_keywords or [],
            complementary_categories=row.complementary_categories or [],
        )

        # Build content
        content = ProductContent(
            seo_title=row.seo_title,
            meta_description=row.meta_description,
            short_description=row.short_description,
            marketing_highlights=row.marketing_highlights or [],
            image_alt_text=row.image_alt_text,
        )

        # Build metadata
        metadata = EnrichmentMetadata(
            model=row.model,
            version=row.version,
            enriched_at=row.enriched_at,
        )

        return ProductEnrichment(
            product_id=row.product_id,
            attributes=attributes,
            categorization=categorization,
            content=content,
            metadata=metadata,
        )
