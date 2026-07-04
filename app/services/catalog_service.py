"""
Servicio de catálogo
"""

from math import ceil
from app.repositories import product_repository
from app.schemas.product import ProductPage, SupermarketInfo
from app.scrapers import SUPERMARKETS

def get_supermarkets(name: str | None = None) -> list[SupermarketInfo]:
    """Estado del catálogo de cada supermercado
    Con name, solo los supermercados cuyo nombre lo contenga"""
    nombres = SUPERMARKETS
    if name:
        nombres = [s for s in nombres if name.lower() in s]
    return [
        SupermarketInfo(
            name=s,
            product_count=product_repository.count_products(s),
            last_scraped_at=product_repository.last_scraped_at(s),
        )
        for s in nombres
    ]


def get_products(
    supermarket: str | None,
    q: str | None,
    category: str | None,
    page: int,
    page_size: int,
) -> ProductPage:
    """Búsqueda paginada de productos"""
    total, items = product_repository.search_products(supermarket, q, category, page, page_size)
    return ProductPage(
        total=total,
        page=page,
        page_size=page_size,
        pages=max(ceil(total / page_size), 1),
        items=items,
    )
