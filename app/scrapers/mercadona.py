"""
Scraper de Mercadona
"""

import asyncio
import logging
import httpx
from app.schemas.product import Product
from app.scrapers.http import get_json

logger = logging.getLogger(__name__) # logger

API = "https://tienda.mercadona.es/api" # URL base de la API de Mercadona

# scrape descarga y devuelve el catálogo completo de Mercadona, ya normalizado
async def scrape(client: httpx.AsyncClient) -> list[Product]:
    arbol = await get_json(client, f"{API}/categories/", lang="es")
    ids = [sub["id"] for categoria in arbol["results"] for sub in categoria["categories"]]

    productos: dict[str, Product] = {}
    fallidas: list[int] = []
    limite = asyncio.Semaphore(5)  # máximo 5 peticiones a la vez

    async def bajar_categoria(categoria_id: int) -> None:
        async with limite:
            try:
                data = await get_json(client, f"{API}/categories/{categoria_id}/", lang="es")
            except httpx.HTTPError:
                fallidas.append(categoria_id)
                return
        for producto in _parsear_categoria(data):
            productos.setdefault(producto.id, producto)

    await asyncio.gather(*(bajar_categoria(i) for i in ids))

    # Mercadona corta si vas rápido: las categorías que fallaron se
    # reintentan al final, de una en una y con pausa
    for categoria_id in fallidas:
        await asyncio.sleep(10)
        try:
            data = await get_json(client, f"{API}/categories/{categoria_id}/", lang="es")
        except httpx.HTTPError as error:
            logger.error("Categoría %s perdida: %s", categoria_id, error)
            continue
        for producto in _parsear_categoria(data):
            productos.setdefault(producto.id, producto)

    return list(productos.values())

# _parsear_categoria normaliza los productos de una categoría de la API de Mercadona a nuestro esquema Product
def _parsear_categoria(data: dict) -> list[Product]:
    resultado = []
    for seccion in data.get("categories", []):
        for p in seccion.get("products", []):
            precio = p.get("price_instructions") or {}
            # La API de listado no trae descripción: se compone con el
            # envase y el tamaño (ej. "Garrafa 5 l").
            trozos = [p.get("packaging")]
            if precio.get("unit_size") and precio.get("size_format"):
                trozos.append(f"{precio['unit_size']:g} {precio['size_format']}")
            resultado.append(
                Product(
                    id=str(p["id"]),
                    supermarket="mercadona",
                    name=p.get("display_name") or "",
                    description=" ".join(t for t in trozos if t) or None,
                    price=_a_float(precio.get("unit_price")),
                    price_per_unit=_a_float(precio.get("reference_price")),
                    unit=precio.get("reference_format"),
                    image_url=p.get("thumbnail"),
                    category=data.get("name"),
                    url=p.get("share_url"),
                )
            )
    return resultado

# _a_float convierte un valor a float, devolviendo None si no es posible
def _a_float(valor) -> float | None:
    try:
        return float(valor) if valor is not None else None
    except (TypeError, ValueError):
        return None
