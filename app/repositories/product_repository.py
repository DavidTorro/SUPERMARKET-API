"""
Capa de repositorio
"""

from datetime import datetime, timezone
from sqlalchemy import delete, func, or_, select
from app.core.database import SessionLocal
from app.models.product import ProductRow
from app.repositories import backup_repository
from app.schemas.product import Product

# Metodo de conveniencia para guardar el catálogo completo de un supermercado
def save_catalog(supermarket: str, products: list[Product]) -> None:
    """Borra el catálogo anterior del supermercado y guarda el nuevo,
    todo en una transacción (si algo falla a medias, no se pierde nada)"""
    now = datetime.now(timezone.utc)

    rows = [
        ProductRow(
            external_id=product.id,
            scraped_at=now,
            **product.model_dump(exclude={"id"}),
        )
        for product in products
    ]

    with SessionLocal() as session, session.begin():
        # Backup del catálogo actual ANTES de borrarlo. Va en la misma
        # transacción: si algo falla, no hay ni backup ni reemplazo.
        backup_repository.create_backup(session, supermarket)
        session.execute(delete(ProductRow).where(ProductRow.supermarket == supermarket))
        session.add_all(rows)


# Contar productos de un supermercado
def count_products(supermarket: str) -> int:
    with SessionLocal() as session:
        query = select(func.count()).select_from(ProductRow)
        return session.scalar(query.where(ProductRow.supermarket == supermarket)) or 0

# Obtener la fecha del último scraping de un supermercado
def last_scraped_at(supermarket: str) -> datetime | None:
    with SessionLocal() as session:
        return session.scalar(
            select(func.max(ProductRow.scraped_at)).where(ProductRow.supermarket == supermarket)
        )

# Buscar productos con filtros y paginación
def search_products(
    supermarket: str | None,
    q: str | None,
    category: str | None,
    page: int,
    page_size: int,
) -> tuple[int, list[Product]]:
    """Devuelve (total de resultados, productos de la página pedida)
    Los filtros se aplican en SQL, que con los índices de la tabla es
    mucho más rápido que traer todo y filtrar en Python"""
    filtros = []
    if supermarket:
        filtros.append(ProductRow.supermarket == supermarket)
    if q:
        buscado = f"%{q}%"
        filtros.append(
            or_(
                ProductRow.name.ilike(buscado),
                ProductRow.description.ilike(buscado),
                ProductRow.brand.ilike(buscado),
            )
        )
    if category:
        filtros.append(ProductRow.category.ilike(f"%{category}%"))

    with SessionLocal() as session:
        total = session.scalar(
            select(func.count()).select_from(ProductRow).where(*filtros)
        ) or 0
        rows = session.scalars(
            select(ProductRow)
            .where(*filtros)
            .order_by(ProductRow.supermarket, ProductRow.name)
            .offset((page - 1) * page_size)  # salta las páginas anteriores
            .limit(page_size)
        ).all()
    return total, [row.to_schema() for row in rows]
