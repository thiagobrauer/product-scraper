"""Use case for enriching product data using AI."""
from typing import Optional
from datetime import datetime, timezone

from src.core.dependencies.log_interface import LogInterface
from src.core.modules.products.enrich_product.gateways.ai_gateway import AIGateway
from src.core.modules.products.enrich_product.gateways.enrichment_repository_gateway import (
    EnrichmentRepositoryGateway,
)
from src.core.modules.products.enrich_product.inputs.enrich_product_input import (
    EnrichProductInput,
)
from src.core.modules.products.enrich_product.responses.enrich_product_response import (
    EnrichProductResponse,
)
from src.core.modules.products.enrich_product.responses.enrich_product_success import (
    EnrichProductSuccess,
)
from src.core.modules.products.enrich_product.responses.enrich_product_error import (
    EnrichProductError,
)
from src.core.modules.products.enrich_product.actions.extract_attributes_action import (
    ExtractAttributesAction,
)
from src.core.modules.products.enrich_product.actions.categorize_product_action import (
    CategorizeProductAction,
)
from src.core.modules.products.enrich_product.actions.generate_content_action import (
    GenerateContentAction,
)
from src.core.modules.products.enrich_product.entities.product_enrichment import (
    ProductEnrichment,
    EnrichmentMetadata,
)
from src.core.modules.products.enrich_product.exceptions.ai_gateway_exception import (
    AIGatewayException,
)


class EnrichProductUseCase:
    """
    Use case for enriching product data using AI.

    This use case orchestrates three AI calls to enrich product data:
    1. Extract structured attributes (sleeve type, neckline, material, etc.)
    2. Generate categorization and tags (occasions, seasons, keywords)
    3. Generate marketing content (SEO title, descriptions, highlights)

    The enrichment data can optionally be saved to a repository.
    """

    def __init__(
        self,
        ai_gateway: AIGateway,
        log: LogInterface,
        enrichment_repository: Optional[EnrichmentRepositoryGateway] = None,
    ):
        """
        Initialize the use case with required dependencies.

        Args:
            ai_gateway: AI service adapter for enrichment calls
            log: Logger for tracking progress
            enrichment_repository: Optional repository for persisting enrichments
        """
        self.ai = ai_gateway
        self.log = log
        self.enrichment_repository = enrichment_repository

        # Initialize actions with AI gateway and logger
        self.extract_attributes = ExtractAttributesAction(ai_gateway, log)
        self.categorize_product = CategorizeProductAction(ai_gateway, log)
        self.generate_content = GenerateContentAction(ai_gateway, log)

    def apply(self, input_data: EnrichProductInput) -> EnrichProductResponse:
        """
        Execute the product enrichment use case.

        Args:
            input_data: Input containing product data and optional product ID

        Returns:
            EnrichProductSuccess with enrichment data on success,
            EnrichProductError with error details on failure
        """
        try:
            product_name = input_data.product_data.get("name", "Unknown")
            self.log.info(
                "Starting product enrichment",
                {
                    "model": self.ai.model_name,
                    "product_name": product_name,
                },
            )

            # Step 1: Extract attributes
            self.log.info("Step 1/3: Extracting attributes")
            attributes = self.extract_attributes.apply(input_data.product_data)

            # Step 2: Generate categorization
            self.log.info("Step 2/3: Generating categorization")
            categorization = self.categorize_product.apply(input_data.product_data)

            # Step 3: Generate content
            self.log.info("Step 3/3: Generating content")
            content = self.generate_content.apply(input_data.product_data)

            # Build enrichment entity
            enrichment = ProductEnrichment(
                product_id=input_data.product_id,
                attributes=attributes,
                categorization=categorization,
                content=content,
                metadata=EnrichmentMetadata(
                    model=self.ai.model_name,
                    version="1.0",
                    enriched_at=datetime.now(timezone.utc),
                ),
            )

            # Save to repository if available
            if self.enrichment_repository and input_data.product_id:
                self.log.info(
                    "Saving enrichment to database",
                    {"product_id": input_data.product_id},
                )
                enrichment = self.enrichment_repository.save(enrichment)
                self.log.info("Enrichment saved successfully")

            self.log.info(
                "Product enrichment completed successfully",
                {"product_name": product_name},
            )

            return EnrichProductSuccess(enrichment=enrichment)

        except AIGatewayException as e:
            self.log.error("AI API error during enrichment", {"error": str(e)})
            return EnrichProductError(
                error_type="ai_error",
                message=str(e),
                step="ai_call",
            )

        except Exception as e:
            self.log.error("Unexpected error during enrichment", {"error": str(e)})
            return EnrichProductError(
                error_type="unexpected_error",
                message=str(e),
            )
