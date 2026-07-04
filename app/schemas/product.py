"""
Esquemas de los productos
"""

from datetime import datetime
from pydantic import BaseModel, Field

class Product(BaseModel):
    """Producto normalizado, igual para todos los supermercados"""

    id: str = Field(
        description="Product ID (unique within a supermarket)",
    )
    supermarket: str = Field(
        description="Supermarket of origin: mercadona, consum or masymas",
    )
    name: str = Field(
        description="Product name",
    )
    description: str | None = Field(
        default=None,
        description="Product description",
    )
    brand: str | None = Field(
        default=None,
        description="Brand (Mercadona doesn't return it)",
    )
    price: float | None = Field(
        default=None,
        description="Current estimated price in EUR",
    )
    price_per_unit: float | None = Field(
        default=None,
        description="Price per reference unit in EUR (per Kg, per L...)",
    )
    unit: str | None = Field(
        default=None,
        description="Reference unit of the previous price ('1 Kg', 'L'...)",
    )
    image_url: str | None = Field(
        default=None,
        description="URL of the product photo",
    )
    category: str | None = Field(
        default=None,
        description="Category within the supermarket",
    )
    ean: str | None = Field(
        default=None,
        description="EAN barcode, if the API returns it",
    )
    url: str | None = Field(
        default=None,
        description="URL of the product page in the store's website",
    )


class ProductFilter(BaseModel):
    """Criterios de búsqueda para el método QUERY

    Es el equivalente a los query params de GET /products, pero
    viajando en el cuerpo de la petición como JSON"""

    supermarket: str | None = Field(
        default=None,
        description="Filter by supermarket",
    )
    q: str | None = Field(
        default=None,
        description="Search in name, description or brand",
    )
    category: str | None = Field(
        default=None,
        description="Filter by category",
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page, starting at 1",
    )
    page_size: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Results per page (maximum 500)",
    )


class SupermarketFilter(BaseModel):
    """Criterios de búsqueda para QUERY /supermarkets"""

    name: str | None = Field(
        default=None,
        description="Filter by supermarket name (partial)",
    )


class ScrapeStatusFilter(BaseModel):
    """Criterios de búsqueda para QUERY /scrape/status"""

    supermarket: str | None = Field(
        default=None,
        description="Filter by supermarket",
    )
    status: str | None = Field(
        default=None,
        description="Filter by status: idle | running | completed | failed",
    )


class ProductPage(BaseModel):
    """Respuesta paginada de GET /products"""

    total: int = Field(
        description="Number of products matching the filter",
    )
    page: int = Field(
        description="Current page, starting at 1",
    )
    page_size: int = Field(
        description="Results per page",
    )
    pages: int = Field(
        description="Total number of pages",
    )
    items: list[Product] = Field(
        description="Products in the current page",
    )


class SupermarketInfo(BaseModel):
    """Estado del catálogo almacenado de un supermercado"""

    name: str = Field(
        description="Supermarket name",
    )
    product_count: int = Field(
        description="Number of products stored in the database",
    )
    last_scraped_at: datetime | None = Field(
        default=None,
        description="Date of the last completed scraping (None if never scraped)",
    )


class ScrapeJob(BaseModel):
    """Estado de un trabajo de scraping"""

    supermarket: str = Field(
        description="Supermarket to which the job belongs",
    )
    status: str = Field(
        default="idle",
        description="Status: idle | running | completed | failed",
    )
    products_scraped: int = Field(
        default=0,
        description="Products obtained in the last completed scraping",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the job started",
    )
    finished_at: datetime | None = Field(
        default=None,
        description="When the job finished (successfully or not)",
    )
    error: str | None = Field(
        default=None,
        description="Error message if the job failed",
    )
