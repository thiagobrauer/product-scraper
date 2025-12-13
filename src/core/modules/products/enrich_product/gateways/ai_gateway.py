"""Gateway protocol for AI operations."""
from typing import Protocol, Dict, Any


class AIGateway(Protocol):
    """
    Protocol defining AI API operations.

    Each AI provider (Claude, OpenAI, etc.) should have
    its own adapter implementing this protocol.
    """

    @property
    def model_name(self) -> str:
        """Return the name of the AI model being used."""
        ...

    def complete(self, prompt: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a prompt to the AI with product data and get structured response.

        Args:
            prompt: The system prompt with instructions
            product_data: The product information to analyze

        Returns:
            Parsed JSON response from the AI

        Raises:
            AIGatewayException: If the API call fails or response is invalid
        """
        ...
