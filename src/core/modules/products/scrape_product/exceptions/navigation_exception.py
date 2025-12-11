"""Exception raised when navigation fails."""


class NavigationException(Exception):
    """Raised when browser navigation fails."""

    def __init__(self, url: str, reason: str = ""):
        self.url = url
        self.reason = reason
        message = f'Failed to navigate to: "{url}"'
        if reason:
            message += f" - {reason}"
        super().__init__(message)
