"""Action to generate categorization and tags for product using AI."""
from typing import Dict, Any

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.enrich_product.gateways.ai_gateway import AIGateway
from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductCategorization,
    TargetAudience,
)


CATEGORIZATION_PROMPT = """You are a product categorization specialist for an e-commerce platform. Generate relevant tags and categorizations to improve product discoverability.

Based on the product information, generate:
- Occasions: when/where this product would be used
- Seasons: which seasons this is appropriate for
- Style tags: descriptive style attributes
- Target audience: who this product is for
- Search keywords: terms customers might use to find this
- Complementary categories: related product categories

Be specific and practical. Only include relevant tags. Respond in JSON:
{
  "occasions": string[],
  "seasons": string[],
  "style_tags": string[],
  "target_audience": {
    "gender": "male" | "female" | "unisex" | "boys" | "girls" | "kids",
    "age_group": "baby" | "toddler" | "child" | "teen" | "adult" | "senior",
    "age_range": string | null
  },
  "search_keywords": string[],
  "complementary_categories": string[]
}"""


class CategorizeProductAction:
    """Generate categorization and tags for a product using AI analysis."""

    def __init__(self, ai_gateway: AIGateway, log: LogInterface):
        self.ai = ai_gateway
        self.log = log

    def apply(self, product_data: Dict[str, Any]) -> ProductCategorization:
        """
        Generate product categorization using AI.

        Args:
            product_data: Dictionary containing product information

        Returns:
            ProductCategorization entity with generated data
        """
        self.log.info("Generating product categorization using AI")

        # Prepare relevant product data for the prompt
        input_data = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "category": product_data.get("category"),
            "brand": product_data.get("brand"),
            "color": product_data.get("color"),
        }

        # Call AI to generate categorization
        response = self.ai.complete(CATEGORIZATION_PROMPT, input_data)

        # Convert response to entity
        categorization = self._parse_response(response)

        self.log.info(
            "Product categorization generated",
            {
                "occasions_count": len(categorization.occasions),
                "keywords_count": len(categorization.search_keywords),
            },
        )

        return categorization

    def _parse_response(self, response: Dict[str, Any]) -> ProductCategorization:
        """Parse AI response into ProductCategorization entity."""
        audience_data = response.get("target_audience", {})
        target_audience = None
        if audience_data:
            target_audience = TargetAudience(
                gender=audience_data.get("gender"),
                age_group=audience_data.get("age_group"),
                age_range=audience_data.get("age_range"),
            )

        return ProductCategorization(
            occasions=response.get("occasions", []),
            seasons=response.get("seasons", []),
            style_tags=response.get("style_tags", []),
            target_audience=target_audience,
            search_keywords=response.get("search_keywords", []),
            complementary_categories=response.get("complementary_categories", []),
        )
