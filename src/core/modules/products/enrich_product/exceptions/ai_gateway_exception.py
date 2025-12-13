"""Exception for AI Gateway errors."""


class AIGatewayException(Exception):
    """Exception raised when AI API operations fail."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message}: {str(self.original_error)}"
        return self.message
