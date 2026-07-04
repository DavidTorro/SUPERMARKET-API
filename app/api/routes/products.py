"""
Router de productos
"""

from fastapi import APIRouter, HTTPException, Query
from app.schemas.product import ( ProductFilter, ProductPage, SupermarketFilter, SupermarketInfo )
from app.scrapers import SUPERMARKETS
from app.services import catalog_service

router = APIRouter(tags=["products"]) # Declaración del router

# GET de supermercados con un modelo de respuesta de lista de SupermarketInfo
@router.get("/supermarkets", response_model=list[SupermarketInfo])
def supermarkets() -> list[SupermarketInfo]:
    return catalog_service.get_supermarkets() # Supermercados disponibles y estado de su catálogo

# QUERY de supermercados filtros opcionales en el body (Nuevo metodo HTTP) de momento uso api_route por que no hay un decorador para QUERY en FastAPI
@router.api_route("/supermarkets", methods=["QUERY"], response_model=list[SupermarketInfo])
# Filtros opcionales en el body (Nuevo metodo HTTP) y la respuesta es una lista de SupermarketInfo
def query_supermarkets(filters: SupermarketFilter | None = None) -> list[SupermarketInfo]: 
    return catalog_service.get_supermarkets(
        name=filters.name if filters else None, # Si filters es None, se pasa None, si no, se pasa filters.name
    )

# GET de productos con filtros en query params y paginación
@router.get("/products", response_model=ProductPage)
def products(
    supermarket: str | None = Query(None, description="mercadona, consum or masymas"),
    q: str | None = Query(None, description="Search in name, description or brand"),
    category: str | None = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
) -> ProductPage:
    if supermarket and supermarket not in SUPERMARKETS:
        raise HTTPException(404, f"Supermarket not found: {supermarket}")
    return catalog_service.get_products(supermarket, q, category, page, page_size) # Lista los productos guardados, con filtros y paginación

# QUERY de productos es como un GET pero con los filtros en el body
@router.api_route("/products", methods=["QUERY"], response_model=ProductPage)
def query_products(filters: ProductFilter) -> ProductPage:
    if filters.supermarket and filters.supermarket not in SUPERMARKETS:
        raise HTTPException(404, f"Supermarket not found: {filters.supermarket}")
    # "Body" de la petición es un objeto ProductFilter, que contiene los filtros opcionales para la búsqueda de productos
    return catalog_service.get_products(
        filters.supermarket,
        filters.q,
        filters.category,
        filters.page,
        filters.page_size,
    )
