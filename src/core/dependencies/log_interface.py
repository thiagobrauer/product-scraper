"""Log interface protocol for dependency injection."""
from typing import Protocol, Dict, Any


class LogInterface(Protocol):
    """Protocol for logging operations."""

    def info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log an info message."""
        ...

    def error(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log an error message."""
        ...

    def debug(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log a debug message."""
        ...
