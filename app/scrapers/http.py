"""
Utilidades HTTP compartidas por todos los scrapers
"""

import asyncio
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__) # logger

def new_client() -> httpx.AsyncClient:
    """Cliente HTTP con los ajustes comunes (timeout, user-agent)"""
    return httpx.AsyncClient(
        timeout=30,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    )

async def get_json(client: httpx.AsyncClient, url: str, **params):
    """GET que reintenta hasta 3 veces con espera creciente entre intentos"""
    for intento in range(3):
        try:
            respuesta = await client.get(url, params=params or None)
            respuesta.raise_for_status()
            return respuesta.json()
        except httpx.HTTPError as error:
            if intento == 2:  # tercer fallo: se rinde y avisa a quien llamó
                raise
            logger.warning("Fallo en %s (intento %d): %s", url, intento + 1, error)
            await asyncio.sleep(2 * (intento + 1))
