"""Action to extract product details from a product page."""
import re
from typing import Optional, List, Dict, Any

from src.core.modules.products.scrape_product.gateways.browser_gateway import (
    BrowserGateway,
)
from src.core.modules.products.scrape_product.entities.product import Product


class ExtractProductDetailsAction:
    """Extract all product details from the current product page."""

    NAME_SELECTORS = ["h1", "[data-testid='product-name']", "[class*='ProductName']"]

    def __init__(self, browser_gateway: BrowserGateway):
        self.browser_gateway = browser_gateway

    def apply(self) -> Product:
        """
        Extract all available product details from the current page.

        Returns:
            A Product entity with all extracted details
        """
        json_ld_data = self.browser_gateway.extract_json_ld()

        name = self._extract_name(json_ld_data)
        price = self._extract_price(json_ld_data)
        original_price = self._extract_original_price(json_ld_data)
        sku = self._extract_sku(json_ld_data)
        brand = self._extract_brand(json_ld_data)
        description = self._extract_description(json_ld_data)
        images = self._extract_images(json_ld_data)
        sizes = self._extract_sizes(json_ld_data)
        color = self._extract_color(json_ld_data, name)
        category = self._extract_category(json_ld_data)
        material = self._extract_material(description)

        return Product(
            name=name or "Unknown Product",
            price=price,
            original_price=original_price,
            description=description,
            image_url=images[0] if images else None,
            images=images if images else None,
            url=self.browser_gateway.get_current_url(),
            sku=sku,
            brand=brand,
            category=category,
            color=color,
            sizes=sizes if sizes else None,
            material=material,
        )

    def _extract_name(self, json_ld_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract product name from JSON-LD or DOM."""
        if json_ld_data:
            name = json_ld_data.get("name")
            if name:
                return name

        for selector in self.NAME_SELECTORS:
            element = self.browser_gateway.query_selector(selector)
            if element:
                name = self.browser_gateway.get_element_text(element).strip()
                if name:
                    return name

        return None

    def _extract_price(self, json_ld_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract current price from JSON-LD."""
        if not json_ld_data:
            return None

        # Try direct offers first
        if "offers" in json_ld_data:
            offers = json_ld_data["offers"]
            if isinstance(offers, dict):
                price_value = offers.get("price") or offers.get("lowPrice")
                if price_value:
                    return f"R${price_value}"
            elif isinstance(offers, list) and offers:
                price_value = offers[0].get("price")
                if price_value:
                    return f"R${price_value}"

        # For ProductGroup, get price from first variant
        if "hasVariant" in json_ld_data:
            variants = json_ld_data["hasVariant"]
            if isinstance(variants, list) and variants:
                first_variant = variants[0]
                if "offers" in first_variant:
                    offers = first_variant["offers"]
                    if isinstance(offers, dict):
                        price_value = offers.get("price")
                        if price_value:
                            return f"R${price_value}"

        return None

    def _extract_original_price(
        self, json_ld_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract original price (list price) from JSON-LD."""
        if not json_ld_data or "offers" not in json_ld_data:
            return None

        offers = json_ld_data["offers"]
        if isinstance(offers, dict):
            list_price = offers.get("highPrice")
            if list_price and str(list_price) != str(offers.get("lowPrice", "")):
                return f"R${list_price}"

        return None

    def _extract_sku(self, json_ld_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract SKU from JSON-LD or URL."""
        if json_ld_data:
            sku = json_ld_data.get("sku")
            if sku:
                return sku

        current_url = self.browser_gateway.get_current_url()
        if "_" in current_url:
            sku_match = re.search(r"-(\d{8})_", current_url)
            if sku_match:
                return sku_match.group(1)

        return None

    def _extract_brand(self, json_ld_data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract brand from JSON-LD."""
        if not json_ld_data or "brand" not in json_ld_data:
            return None

        brand_data = json_ld_data["brand"]
        if isinstance(brand_data, dict):
            return brand_data.get("name")
        elif isinstance(brand_data, str):
            return brand_data

        return None

    def _extract_description(
        self, json_ld_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract and clean description from JSON-LD."""
        if not json_ld_data:
            return None

        desc = json_ld_data.get("description", "")
        if not desc:
            return None

        # Clean HTML tags from description
        description = re.sub(r"<[^>]+>", " ", desc)
        description = re.sub(r"&nbsp;", " ", description)
        description = re.sub(r"\s+", " ", description).strip()

        return description

    def _extract_images(
        self, json_ld_data: Optional[Dict[str, Any]]
    ) -> Optional[List[str]]:
        """Extract images from JSON-LD or DOM."""
        images = []

        if json_ld_data and "image" in json_ld_data:
            img_data = json_ld_data["image"]
            if isinstance(img_data, list):
                images = img_data
            elif isinstance(img_data, str):
                images = [img_data]

        # Fallback: get images from page
        if not images:
            all_imgs = self.browser_gateway.query_selector_all(
                "img[src*='static.riachuelo']"
            )
            for img in all_imgs:
                src = self.browser_gateway.get_element_attribute(img, "src")
                if src and src not in images and "portrait" in src:
                    images.append(src)

        return images if images else None

    def _extract_sizes(
        self, json_ld_data: Optional[Dict[str, Any]]
    ) -> Optional[List[str]]:
        """Extract available sizes from JSON-LD variants."""
        if not json_ld_data or "hasVariant" not in json_ld_data:
            return None

        sizes = []
        variants = json_ld_data["hasVariant"]

        if isinstance(variants, list):
            for variant in variants:
                size = variant.get("size")
                if size and size not in sizes:
                    sizes.append(size)

            # Sort sizes numerically if possible
            try:
                sizes = sorted(sizes, key=lambda x: int(x))
            except ValueError:
                sizes = sorted(sizes)

        return sizes if sizes else None

    def _extract_color(
        self, json_ld_data: Optional[Dict[str, Any]], name: Optional[str]
    ) -> Optional[str]:
        """Extract color from JSON-LD or product name."""
        if json_ld_data:
            color = json_ld_data.get("color")
            if color:
                return color

        if name and " - " in name:
            return name.split(" - ")[-1].strip()

        return None

    def _extract_category(
        self, json_ld_data: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Extract category from JSON-LD or breadcrumbs."""
        if json_ld_data and "category" in json_ld_data:
            return json_ld_data["category"]

        # Try to extract from breadcrumbs
        breadcrumbs = self.browser_gateway.query_selector_all(
            "nav[aria-label='breadcrumb'] a"
        )
        if breadcrumbs:
            category_parts = []
            for bc in breadcrumbs[1:]:  # Skip "Home"
                text = self.browser_gateway.get_element_text(bc).strip()
                if text:
                    category_parts.append(text)
            if category_parts:
                return " > ".join(category_parts)

        return None

    def _extract_material(self, description: Optional[str]) -> Optional[str]:
        """Extract material composition from description."""
        if not description:
            return None

        # Match pattern: Material percentage; Material percentage
        material_match = re.search(
            r"([A-Za-záéíóúãõâêîôûç\s]+\d+%(?:;\s*[A-Za-záéíóúãõâêîôûç\s]+\d+%)*)",
            description,
        )
        if material_match:
            return material_match.group(1).strip()

        return None
