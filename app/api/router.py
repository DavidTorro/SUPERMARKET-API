"""
Router de la API
"""

from fastapi import APIRouter
from app.api.routes import backups, products, scrape

api_router = APIRouter() # Router principal de la API, que incluye los routers de productos, scraping y backups

api_router.include_router(products.router)
api_router.include_router(scrape.router)
api_router.include_router(backups.router)
