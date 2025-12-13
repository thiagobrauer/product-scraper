"""Action to generate marketing content for product using AI."""
from typing import Dict, Any

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.enrich_product.gateways.ai_gateway import AIGateway
from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductContent,
)


CONTENT_GENERATION_PROMPT = """You are a marketing copywriter for an e-commerce platform. Generate optimized content for the product provided.

Create:
1. SEO title: max 60 characters, include key attributes and brand
2. Meta description: max 155 characters, compelling and keyword-rich
3. Short description: 1-2 sentences for product cards
4. Marketing highlights: 3-5 bullet points for product page
5. Alt text: accessible image description

Write in the same language as the original product. Be accurate - don't invent features not mentioned in the source.

Respond in JSON:
{
  "seo_title": string,
  "meta_description": string,
  "short_description": string,
  "marketing_highlights": string[],
  "image_alt_text": string
}"""


class GenerateContentAction:
    """Generate marketing content for a product using AI analysis."""

    def __init__(self, ai_gateway: AIGateway, log: LogInterface):
        self.ai = ai_gateway
        self.log = log

    def apply(self, product_data: Dict[str, Any]) -> ProductContent:
        """
        Generate marketing content using AI.

        Args:
            product_data: Dictionary containing product information

        Returns:
            ProductContent entity with generated content
        """
        self.log.info("Generating marketing content using AI")

        # Prepare relevant product data for the prompt
        input_data = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "brand": product_data.get("brand"),
            "color": product_data.get("color"),
            "material": product_data.get("material"),
            "category": product_data.get("category"),
        }

        # Call AI to generate content
        response = self.ai.complete(CONTENT_GENERATION_PROMPT, input_data)

        # Convert response to entity
        content = self._parse_response(response)

        self.log.info(
            "Marketing content generated",
            {"highlights_count": len(content.marketing_highlights)},
        )

        return content

    def _parse_response(self, response: Dict[str, Any]) -> ProductContent:
        """Parse AI response into ProductContent entity."""
        return ProductContent(
            seo_title=response.get("seo_title"),
            meta_description=response.get("meta_description"),
            short_description=response.get("short_description"),
            marketing_highlights=response.get("marketing_highlights", []),
            image_alt_text=response.get("image_alt_text"),
        )
