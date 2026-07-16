"""
Capa de scrapers
"""

from app.schemas.product import Product
from app.scrapers import aktios, lidl, mercadona
from app.scrapers.http import new_client

SUPERMARKETS = ["mercadona", "consum", "masymas", "lidl"]

async def scrape(supermarket: str) -> list[Product]:
    async with new_client() as client:
        if supermarket == "mercadona":
            return await mercadona.scrape(client)
        if supermarket == "consum":
            return await aktios.scrape(client, "consum", "https://tienda.consum.es")
        if supermarket == "masymas":
            return await aktios.scrape(client, "masymas", "https://tienda.masymas.com")
        if supermarket == "lidl":
            return await lidl.scrape(client)
        raise ValueError(f"Supermarket not found: {supermarket}")
