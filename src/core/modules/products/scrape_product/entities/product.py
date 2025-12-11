"""Product entity representing a scraped product."""
from typing import Optional, List, Dict, Any


class Product:
    """Represents a scraped product with all its details."""

    def __init__(
        self,
        name: str,
        price: Optional[str] = None,
        original_price: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        images: Optional[List[str]] = None,
        url: Optional[str] = None,
        sku: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        color: Optional[str] = None,
        sizes: Optional[List[str]] = None,
        material: Optional[str] = None,
        specifications: Optional[Dict[str, str]] = None,
    ):
        self._name = name
        self._price = price
        self._original_price = original_price
        self._description = description
        self._image_url = image_url
        self._images = images or []
        self._url = url
        self._sku = sku
        self._brand = brand
        self._category = category
        self._color = color
        self._sizes = sizes or []
        self._material = material
        self._specifications = specifications or {}
        self._enriched_data: Optional[Dict[str, Any]] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> Optional[str]:
        return self._price

    @property
    def original_price(self) -> Optional[str]:
        return self._original_price

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def image_url(self) -> Optional[str]:
        return self._image_url

    @property
    def images(self) -> List[str]:
        return self._images

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def sku(self) -> Optional[str]:
        return self._sku

    @property
    def brand(self) -> Optional[str]:
        return self._brand

    @property
    def category(self) -> Optional[str]:
        return self._category

    @property
    def color(self) -> Optional[str]:
        return self._color

    @property
    def sizes(self) -> List[str]:
        return self._sizes

    @property
    def material(self) -> Optional[str]:
        return self._material

    @property
    def specifications(self) -> Dict[str, str]:
        return self._specifications

    @property
    def enriched_data(self) -> Optional[Dict[str, Any]]:
        return self._enriched_data

    def set_enriched_data(self, data: Dict[str, Any]) -> "Product":
        """Set AI-enriched data for the product."""
        self._enriched_data = data
        return self

    def has_discount(self) -> bool:
        """Check if product has a discount (original price differs from current price)."""
        return self._original_price is not None and self._original_price != self._price

    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary representation."""
        return {
            "name": self._name,
            "price": self._price,
            "original_price": self._original_price,
            "description": self._description,
            "image_url": self._image_url,
            "images": self._images if self._images else None,
            "url": self._url,
            "sku": self._sku,
            "brand": self._brand,
            "category": self._category,
            "color": self._color,
            "sizes": self._sizes if self._sizes else None,
            "material": self._material,
            "specifications": self._specifications if self._specifications else None,
            "enriched_data": self._enriched_data,
        }
