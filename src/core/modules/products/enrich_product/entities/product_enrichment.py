"""Entity representing AI-enriched product data."""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MaterialParsed:
    """Parsed material information."""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    percentage: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "percentage": self.percentage,
        }


@dataclass
class ProductAttributes:
    """Extracted product attributes from AI analysis."""
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sleeve_type": self.sleeve_type,
            "neckline": self.neckline,
            "fit": self.fit,
            "closure_type": self.closure_type,
            "pattern": self.pattern,
            "heel_height": self.heel_height,
            "toe_style": self.toe_style,
            "uv_protection": self.uv_protection,
            "material_parsed": self.material_parsed.to_dict() if self.material_parsed else None,
            "care_instructions": self.care_instructions,
            "key_features": self.key_features,
        }


@dataclass
class TargetAudience:
    """Target audience information."""
    gender: Optional[str] = None
    age_group: Optional[str] = None
    age_range: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gender": self.gender,
            "age_group": self.age_group,
            "age_range": self.age_range,
        }


@dataclass
class ProductCategorization:
    """Categorization and tagging from AI analysis."""
    occasions: List[str] = field(default_factory=list)
    seasons: List[str] = field(default_factory=list)
    style_tags: List[str] = field(default_factory=list)
    target_audience: Optional[TargetAudience] = None
    search_keywords: List[str] = field(default_factory=list)
    complementary_categories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "occasions": self.occasions,
            "seasons": self.seasons,
            "style_tags": self.style_tags,
            "target_audience": self.target_audience.to_dict() if self.target_audience else None,
            "search_keywords": self.search_keywords,
            "complementary_categories": self.complementary_categories,
        }


@dataclass
class ProductContent:
    """Generated marketing content from AI analysis."""
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    short_description: Optional[str] = None
    marketing_highlights: List[str] = field(default_factory=list)
    image_alt_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seo_title": self.seo_title,
            "meta_description": self.meta_description,
            "short_description": self.short_description,
            "marketing_highlights": self.marketing_highlights,
            "image_alt_text": self.image_alt_text,
        }


@dataclass
class EnrichmentMetadata:
    """Metadata about the enrichment process."""
    model: str
    version: str = "1.0"
    enriched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "version": self.version,
            "enriched_at": self.enriched_at.isoformat(),
        }


class ProductEnrichment:
    """Entity representing complete AI-enriched product data."""

    def __init__(
        self,
        product_id: Optional[int] = None,
        attributes: Optional[ProductAttributes] = None,
        categorization: Optional[ProductCategorization] = None,
        content: Optional[ProductContent] = None,
        metadata: Optional[EnrichmentMetadata] = None,
    ):
        self._product_id = product_id
        self._attributes = attributes or ProductAttributes()
        self._categorization = categorization or ProductCategorization()
        self._content = content or ProductContent()
        self._metadata = metadata

    @property
    def product_id(self) -> Optional[int]:
        return self._product_id

    @property
    def attributes(self) -> ProductAttributes:
        return self._attributes

    @property
    def categorization(self) -> ProductCategorization:
        return self._categorization

    @property
    def content(self) -> ProductContent:
        return self._content

    @property
    def metadata(self) -> Optional[EnrichmentMetadata]:
        return self._metadata

    def set_product_id(self, product_id: int) -> "ProductEnrichment":
        """Set the product ID this enrichment belongs to."""
        self._product_id = product_id
        return self

    def set_attributes(self, attributes: ProductAttributes) -> "ProductEnrichment":
        """Set the extracted attributes."""
        self._attributes = attributes
        return self

    def set_categorization(self, categorization: ProductCategorization) -> "ProductEnrichment":
        """Set the categorization data."""
        self._categorization = categorization
        return self

    def set_content(self, content: ProductContent) -> "ProductEnrichment":
        """Set the generated content."""
        self._content = content
        return self

    def set_metadata(self, metadata: EnrichmentMetadata) -> "ProductEnrichment":
        """Set the enrichment metadata."""
        self._metadata = metadata
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert enrichment to dictionary representation."""
        return {
            "product_id": self._product_id,
            "attributes": self._attributes.to_dict(),
            "categorization": self._categorization.to_dict(),
            "content": self._content.to_dict(),
            "enrichment_metadata": self._metadata.to_dict() if self._metadata else None,
        }
