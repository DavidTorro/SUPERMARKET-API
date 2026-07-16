"""
Scraper de Lidl
"""

import html
import re
import httpx
from app.schemas.product import Product
from app.scrapers.http import get_json

WEB = "https://www.lidl.es" # URL base de la tienda de Lidl
API = f"{WEB}/q/api/search" # API de búsqueda que usa la propia web

# scrape descarga y devuelve el catálogo completo de Lidl, ya normalizado
async def scrape(client: httpx.AsyncClient) -> list[Product]:
    productos: dict[str, Product] = {}

    # Con q vacío la API devuelve el catálogo entero, pero el orden no es
    # estable entre páginas y se pierden productos en los cortes: se hacen
    # dos pasadas (precio ascendente y descendente) y se fusionan por id.
    for orden in ("price", "price-desc"):
        offset = 0
        while True:
            data = await get_json(
                client,
                API,
                assortment="ES",
                locale="es_ES",
                version="v2.0.0",
                q="",
                sort=orden,
                offset=offset,
                fetchsize=100,  # pedir más no sirve: el servidor corta en ~108
            )
            items = data.get("items") or []
            for item in items:
                producto = _parsear_producto(item)
                if producto:
                    productos.setdefault(producto.id, producto)
            offset += 100
            if not items or offset >= data.get("numFound", 0):
                break

    return list(productos.values())

# _parsear_producto normaliza un producto de la API de Lidl a nuestro esquema Product
def _parsear_producto(item: dict) -> Product | None:
    datos = (item.get("gridbox") or {}).get("data") or {}
    nombre = datos.get("fullTitle") or datos.get("title")
    if item.get("resultClass") != "product" or not nombre:
        return None

    precio = datos.get("price") or {}
    por_unidad = precio.get("basePrice") or {}  # ej. {"price": 9.5, "unit": "m"}
    keyfacts = datos.get("keyfacts") or {}

    # La descripción viene en HTML; si no hay, se usa el envase (ej. "1 l")
    descripcion = _sin_html(keyfacts.get("description"))
    if not descripcion:
        descripcion = (precio.get("packaging") or {}).get("text")

    # La categoría es una ruta ("Mundos de necesidad/Comida y.../Leche y nata"):
    # se toma el último tramo, que es el más concreto
    ruta = keyfacts.get("wonCategoryPrimary") or ""
    categoria = ruta.rsplit("/", 1)[-1] or datos.get("category")

    url = datos.get("canonicalUrl")

    return Product(
        id=str(item.get("code") or datos["productId"]),
        supermarket="lidl",
        name=nombre,
        description=descripcion,
        brand=(datos.get("brand") or {}).get("name"),
        price=precio.get("price"),
        price_per_unit=por_unidad.get("price"),
        unit=por_unidad.get("unit"),
        image_url=datos.get("image"),
        category=categoria or None,
        url=f"{WEB}{url}" if url else None,
    )

# _sin_html limpia etiquetas y entidades HTML de un texto
def _sin_html(texto: str | None) -> str | None:
    if not texto:
        return None
    limpio = re.sub(r"<[^>]+>", " ", html.unescape(texto))
    return " ".join(limpio.split()) or None
