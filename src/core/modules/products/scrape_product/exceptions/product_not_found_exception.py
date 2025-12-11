"""Exception raised when a product is not found."""


class ProductNotFoundException(Exception):
    """Raised when no product is found for the given search query."""

    def __init__(self, query: str):
        self.query = query
        super().__init__(f'No product found for query: "{query}"')
