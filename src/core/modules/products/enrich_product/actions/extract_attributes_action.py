"""Action to extract structured attributes from product data using AI."""
from typing import Dict, Any

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.enrich_product.gateways.ai_gateway import AIGateway
from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductAttributes,
    MaterialParsed,
)


ATTRIBUTES_EXTRACTION_PROMPT = """You are a product data specialist. Extract structured attributes from the product information provided.

Analyze the product name, description, and any available metadata. Extract ONLY attributes that are explicitly mentioned or can be confidently inferred. Use null for attributes that cannot be determined.

Respond in JSON format following this schema:
{
  "sleeve_type": "short" | "long" | "sleeveless" | "3/4" | null,
  "neckline": "round" | "v-neck" | "polo" | "high" | "square" | null,
  "fit": "regular" | "slim" | "loose" | "oversized" | null,
  "closure_type": "button" | "zipper" | "buckle" | "elastic" | "tie" | "none" | null,
  "pattern": "solid" | "striped" | "printed" | "floral" | "geometric" | "checkered" | null,
  "heel_height": "flat" | "low" | "medium" | "high" | null,
  "toe_style": "round" | "pointed" | "square" | "open" | null,
  "uv_protection": string | null,
  "material_parsed": {
    "primary": string | null,
    "secondary": string | null,
    "percentage": string | null
  },
  "care_instructions": string[] | null,
  "key_features": string[]
}"""


class ExtractAttributesAction:
    """Extract structured product attributes using AI analysis."""

    def __init__(self, ai_gateway: AIGateway, log: LogInterface):
        self.ai = ai_gateway
        self.log = log

    def apply(self, product_data: Dict[str, Any]) -> ProductAttributes:
        """
        Extract product attributes using AI.

        Args:
            product_data: Dictionary containing product information

        Returns:
            ProductAttributes entity with extracted data
        """
        self.log.info("Extracting product attributes using AI")

        # Prepare relevant product data for the prompt
        input_data = {
            "name": product_data.get("name"),
            "description": product_data.get("description"),
            "material": product_data.get("material"),
            "category": product_data.get("category"),
        }

        # Call AI to extract attributes
        response = self.ai.complete(ATTRIBUTES_EXTRACTION_PROMPT, input_data)

        # Convert response to entity
        attributes = self._parse_response(response)

        self.log.info(
            "Product attributes extracted",
            {"key_features_count": len(attributes.key_features)},
        )

        return attributes

    def _parse_response(self, response: Dict[str, Any]) -> ProductAttributes:
        """Parse AI response into ProductAttributes entity."""
        material_data = response.get("material_parsed")
        material_parsed = None
        if material_data:
            material_parsed = MaterialParsed(
                primary=material_data.get("primary"),
                secondary=material_data.get("secondary"),
                percentage=material_data.get("percentage"),
            )

        return ProductAttributes(
            sleeve_type=response.get("sleeve_type"),
            neckline=response.get("neckline"),
            fit=response.get("fit"),
            closure_type=response.get("closure_type"),
            pattern=response.get("pattern"),
            heel_height=response.get("heel_height"),
            toe_style=response.get("toe_style"),
            uv_protection=response.get("uv_protection"),
            material_parsed=material_parsed,
            care_instructions=response.get("care_instructions"),
            key_features=response.get("key_features", []),
        )
