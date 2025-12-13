"""Claude API adapter for AI enrichment operations."""
import os
import json
import re
from typing import Dict, Any

import anthropic

from src.core.modules.products.enrich_product.gateways.ai_gateway import AIGateway
from src.core.modules.products.enrich_product.exceptions.ai_gateway_exception import (
    AIGatewayException,
)


class ClaudeAIAdapter:
    """
    Adapter that implements AIGateway protocol using Claude API.

    This adapter handles communication with the Anthropic Claude API
    and parses responses into structured JSON data.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 2048

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the Claude API adapter.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var
            model: Model to use. Defaults to claude-sonnet-4-20250514
        """
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise AIGatewayException(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )

        self._model = model or self.DEFAULT_MODEL
        self._client = anthropic.Anthropic(api_key=self._api_key)

    @property
    def model_name(self) -> str:
        """Return the name of the AI model being used."""
        return self._model

    def complete(self, prompt: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a prompt to Claude with product data and get structured response.

        Args:
            prompt: The system prompt with instructions
            product_data: The product information to analyze

        Returns:
            Parsed JSON response from Claude

        Raises:
            AIGatewayException: If the API call fails or response is invalid
        """
        try:
            # Build the user message with product data
            user_message = f"""Analyze this product and respond with ONLY valid JSON (no markdown, no explanation):

Product Data:
{json.dumps(product_data, indent=2, ensure_ascii=False)}"""

            # Call Claude API
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self.MAX_TOKENS,
                system=prompt,
                messages=[{"role": "user", "content": user_message}],
            )

            # Extract text content from response
            response_text = response.content[0].text

            # Parse JSON from response
            return self._parse_json_response(response_text)

        except anthropic.APIError as e:
            raise AIGatewayException(f"Claude API error", e)
        except json.JSONDecodeError as e:
            raise AIGatewayException(f"Failed to parse Claude response as JSON", e)
        except Exception as e:
            raise AIGatewayException(f"Unexpected error during Claude API call", e)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude's response, handling potential formatting issues.

        Args:
            response_text: Raw text response from Claude

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If JSON cannot be parsed
        """
        # Remove potential markdown code blocks
        cleaned = response_text.strip()

        # Remove ```json or ``` markers if present
        if cleaned.startswith("```"):
            # Find the end of the opening marker
            first_newline = cleaned.find("\n")
            if first_newline != -1:
                cleaned = cleaned[first_newline + 1 :]

            # Remove closing ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

        cleaned = cleaned.strip()

        # Try to parse the JSON
        return json.loads(cleaned)
