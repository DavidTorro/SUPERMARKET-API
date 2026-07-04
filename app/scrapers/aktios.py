"""
Scraper de las tiendas Aktios (Consum y Masymas)
"""

import httpx
from app.schemas.product import Product
from app.scrapers.http import get_json

# scrape descarga y devuelve el catálogo completo de Consum, ya normalizado
async def scrape(client: httpx.AsyncClient, supermarket: str, base_url: str) -> list[Product]:
    productos: dict[str, Product] = {}
    offset = 0

    while True:
        data = await get_json(
            client,
            f"{base_url}/api/rest/V1.0/catalog/product",
            limit=100,
            offset=offset,
            showRecommendations="false",
        )
        for p in data.get("products", []):
            producto = _parsear_producto(p, supermarket)
            if producto:
                productos.setdefault(producto.id, producto)
        offset += 100
        if not data.get("hasMore") or not data.get("products"):
            return list(productos.values())

# _parsear_producto normaliza un producto de la API de Aktios a nuestro esquema Product
def _parsear_producto(p: dict, supermarket: str) -> Product | None:
    datos = p.get("productData") or {}
    if not datos.get("name"):
        return None

    # Precio: si hay oferta vigente se usa; si no, el precio normal.
    lista_precios = (p.get("priceData") or {}).get("prices", [])
    precios = {
        entrada.get("id"): entrada.get("value") or {}
        for entrada in lista_precios
    }
    valor = precios.get("OFFER_PRICE") or precios.get("PRICE") or {}

    # Imagen: en Consum el campo imageURL está roto (404) y las buenas
    # están en "media"; en Masymas es al revés (media viene vacío).
    media = sorted(
        (m for m in p.get("media") or [] if m.get("url")),
        key=lambda m: m.get("order", 0),
    )
    imagen = media[0]["url"] if media else datos.get("imageURL")

    categorias = p.get("categories") or []
    
    return Product(
        id=str(p.get("code") or p["id"]),
        supermarket=supermarket,
        name=datos["name"],
        description=datos.get("description"),
        brand=(datos.get("brand") or {}).get("name"),
        price=valor.get("centAmount"),  # pese al nombre, viene en euros
        price_per_unit=valor.get("centUnitAmount"),
        unit=(p.get("priceData") or {}).get("unitPriceUnitType") or None,
        image_url=imagen,
        category=categorias[0].get("name") if categorias else None,
        ean=p.get("ean"),
        url=datos.get("url"),
    )
