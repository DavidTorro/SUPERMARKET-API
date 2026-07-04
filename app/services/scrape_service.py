"""
Servicio de scraping
"""

import asyncio
import logging
from datetime import datetime, timezone
from app import scrapers
from app.repositories import product_repository
from app.schemas.product import ScrapeJob

logger = logging.getLogger(__name__) # logger

# Un trabajo por supermercado
# Al ser un dict en memoria, el estado se reinicia si se reinicia la API (los datos, en cambio, están en BBDD)
jobs: dict[str, ScrapeJob] = {s: ScrapeJob(supermarket=s) for s in scrapers.SUPERMARKETS}

def start_job(supermarket: str) -> ScrapeJob:
    """Arranca el scraping de un supermercado si no está ya en marcha"""
    if jobs[supermarket].status != "running":
        jobs[supermarket] = ScrapeJob(
            supermarket=supermarket, status="running", started_at=datetime.now(timezone.utc)
        )
        asyncio.create_task(_run(supermarket))
    return jobs[supermarket]


def start_all() -> list[ScrapeJob]:
    return [start_job(s) for s in scrapers.SUPERMARKETS]


def get_status(
    supermarket: str | None = None,
    status: str | None = None,
) -> list[ScrapeJob]:
    """Estado de los trabajos, con filtros opcionales"""
    resultado = list(jobs.values())
    if supermarket:
        resultado = [j for j in resultado if j.supermarket == supermarket]
    if status:
        resultado = [j for j in resultado if j.status == status]
    return resultado


async def _run(supermarket: str) -> None:
    """Scrapea y guarda. Se ejecuta en segundo plano"""
    job = jobs[supermarket]
    try:
        products = await scrapers.scrape(supermarket)
        # La escritura en BBDD es síncrona: se manda a un hilo para no
        # bloquear el event loop mientras inserta miles de filas
        await asyncio.to_thread(product_repository.save_catalog, supermarket, products)
        job.status = "completed"
        job.products_scraped = len(products)
        logger.info("[%s] completed: %d products", supermarket, len(products))
    except Exception as error:
        job.status = "failed"
        job.error = str(error)
        logger.exception("[%s] scraping failed", supermarket)
    finally:
        job.finished_at = datetime.now(timezone.utc)
