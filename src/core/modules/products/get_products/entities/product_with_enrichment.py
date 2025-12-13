"""Entity representing a product with its enrichment data."""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MaterialParsed:
    """Parsed material information."""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    percentage: Optional[str] = None


@dataclass
class TargetAudience:
    """Target audience information."""
    gender: Optional[str] = None
    age_group: Optional[str] = None
    age_range: Optional[str] = None


@dataclass
class Attributes:
    """Product attributes from enrichment."""
    sleeve_type: Optional[str] = None
    neckline: Optional[str] = None
    fit: Optional[str] = None
    closure_type: Optional[str] = None
    pattern: Optional[str] = None
    heel_height: Optional[str] = None
    toe_style: Optional[str] = None
    uv_protection: Optional[str] = None
    material_parsed: Optional[MaterialParsed] = None
    care_instructions: Optional[List[str]] = None
    key_features: List[str] = field(default_factory=list)


@dataclass
class Categorization:
    """Product categorization from enrichment."""
    occasions: List[str] = field(default_factory=list)
    seasons: List[str] = field(default_factory=list)
    style_tags: List[str] = field(default_factory=list)
    target_audience: Optional[TargetAudience] = None
    search_keywords: List[str] = field(default_factory=list)
    complementary_categories: List[str] = field(default_factory=list)


@dataclass
class Content:
    """Product content from enrichment."""
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    short_description: Optional[str] = None
    marketing_highlights: List[str] = field(default_factory=list)
    image_alt_text: Optional[str] = None


@dataclass
class EnrichmentMetadata:
    """Metadata about the enrichment."""
    model: Optional[str] = None
    enriched_at: Optional[datetime] = None
    version: Optional[str] = None


@dataclass
class EnrichedData:
    """Complete enrichment data structure."""
    attributes: Optional[Attributes] = None
    categorization: Optional[Categorization] = None
    content: Optional[Content] = None
    enrichment_metadata: Optional[EnrichmentMetadata] = None


@dataclass
class ProductWithEnrichment:
    """Entity representing a product with its enrichment data."""
    id: int
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[str] = None
    original_price: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    images: List[str] = field(default_factory=list)
    url: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    sizes: List[str] = field(default_factory=list)
    material: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    enriched_data: Optional[EnrichedData] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        enriched_data_dict = None
        if self.enriched_data:
            enriched_data_dict = {
                "attributes": {
                    "sleeve_type": self.enriched_data.attributes.sleeve_type if self.enriched_data.attributes else None,
                    "neckline": self.enriched_data.attributes.neckline if self.enriched_data.attributes else None,
                    "fit": self.enriched_data.attributes.fit if self.enriched_data.attributes else None,
                    "closure_type": self.enriched_data.attributes.closure_type if self.enriched_data.attributes else None,
                    "pattern": self.enriched_data.attributes.pattern if self.enriched_data.attributes else None,
                    "heel_height": self.enriched_data.attributes.heel_height if self.enriched_data.attributes else None,
                    "toe_style": self.enriched_data.attributes.toe_style if self.enriched_data.attributes else None,
                    "uv_protection": self.enriched_data.attributes.uv_protection if self.enriched_data.attributes else None,
                    "material_parsed": {
                        "primary": self.enriched_data.attributes.material_parsed.primary,
                        "secondary": self.enriched_data.attributes.material_parsed.secondary,
                        "percentage": self.enriched_data.attributes.material_parsed.percentage,
                    } if self.enriched_data.attributes and self.enriched_data.attributes.material_parsed else None,
                    "care_instructions": self.enriched_data.attributes.care_instructions if self.enriched_data.attributes else None,
                    "key_features": self.enriched_data.attributes.key_features if self.enriched_data.attributes else [],
                } if self.enriched_data.attributes else None,
                "categorization": {
                    "occasions": self.enriched_data.categorization.occasions if self.enriched_data.categorization else [],
                    "seasons": self.enriched_data.categorization.seasons if self.enriched_data.categorization else [],
                    "style_tags": self.enriched_data.categorization.style_tags if self.enriched_data.categorization else [],
                    "target_audience": {
                        "gender": self.enriched_data.categorization.target_audience.gender,
                        "age_group": self.enriched_data.categorization.target_audience.age_group,
                        "age_range": self.enriched_data.categorization.target_audience.age_range,
                    } if self.enriched_data.categorization and self.enriched_data.categorization.target_audience else None,
                    "search_keywords": self.enriched_data.categorization.search_keywords if self.enriched_data.categorization else [],
                    "complementary_categories": self.enriched_data.categorization.complementary_categories if self.enriched_data.categorization else [],
                } if self.enriched_data.categorization else None,
                "content": {
                    "seo_title": self.enriched_data.content.seo_title if self.enriched_data.content else None,
                    "meta_description": self.enriched_data.content.meta_description if self.enriched_data.content else None,
                    "short_description": self.enriched_data.content.short_description if self.enriched_data.content else None,
                    "marketing_highlights": self.enriched_data.content.marketing_highlights if self.enriched_data.content else [],
                    "image_alt_text": self.enriched_data.content.image_alt_text if self.enriched_data.content else None,
                } if self.enriched_data.content else None,
                "enrichment_metadata": {
                    "model": self.enriched_data.enrichment_metadata.model if self.enriched_data.enrichment_metadata else None,
                    "enriched_at": self.enriched_data.enrichment_metadata.enriched_at.isoformat() if self.enriched_data.enrichment_metadata and self.enriched_data.enrichment_metadata.enriched_at else None,
                    "version": self.enriched_data.enrichment_metadata.version if self.enriched_data.enrichment_metadata else None,
                } if self.enriched_data.enrichment_metadata else None,
            }

        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "price": self.price,
            "original_price": self.original_price,
            "description": self.description,
            "image_url": self.image_url,
            "images": self.images,
            "url": self.url,
            "brand": self.brand,
            "category": self.category,
            "color": self.color,
            "sizes": self.sizes,
            "material": self.material,
            "specifications": self.specifications,
            "enriched_data": enriched_data_dict,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
