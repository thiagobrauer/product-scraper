"""Console logger implementation of the LogInterface protocol."""
from typing import Dict, Any, Optional


class ConsoleLoggerAdapter:
    """
    Simple console logger that implements LogInterface.

    Outputs log messages to the console with formatting.
    """

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message."""
        self._log("INFO", message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error message."""
        self._log("ERROR", message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug message."""
        self._log("DEBUG", message, context)

    def _log(
        self, level: str, message: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Internal method to format and print log messages."""
        prefix = f"[{level}]"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            print(f"{prefix} {message} ({context_str})")
        else:
            print(f"{prefix} {message}")
