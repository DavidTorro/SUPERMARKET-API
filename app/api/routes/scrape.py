"""
Router de scraping
"""

from fastapi import APIRouter, HTTPException
from app.schemas.product import ScrapeJob, ScrapeStatusFilter
from app.scrapers import SUPERMARKETS
from app.services import scrape_service

router = APIRouter(prefix="/scrape", tags=["scraping"]) # Declaración del router

# POST de scraping de todos los supermercados, no tiene / por que es el endpoint raíz del router
@router.post("", response_model=list[ScrapeJob], status_code=202)
async def scrape_all() -> list[ScrapeJob]:
    return scrape_service.start_all() # Lanza el scraping de todos los supermercados y devuelve la lista de trabajos iniciados

# GET de status de los trabajos de scraping 
@router.get("/status", response_model=list[ScrapeJob])
def scrape_status() -> list[ScrapeJob]:
    return scrape_service.get_status()


# QUERY de estado con filtros opcionales en el body (Nuevo metodo HTTP) y la respuesta es una lista de ScrapeJob
@router.api_route("/status", methods=["QUERY"], response_model=list[ScrapeJob])
def query_scrape_status(filters: ScrapeStatusFilter | None = None) -> list[ScrapeJob]:
    # "Body" de la petición es un objeto ScrapeStatusFilter, que contiene los filtros opcionales para la búsqueda de trabajos de scraping
    return scrape_service.get_status(
        supermarket=filters.supermarket if filters else None,
        status=filters.status if filters else None,
    )

# POST de scraping de un supermercado concreto, con el nombre del supermercado en la ruta
@router.post("/{supermarket}", response_model=ScrapeJob, status_code=202)
async def scrape_one(supermarket: str) -> ScrapeJob:
    if supermarket not in SUPERMARKETS:
        raise HTTPException(404, f"Supermarket not found: {supermarket}")
    return scrape_service.start_job(supermarket)
