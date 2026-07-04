"""
Repositorio de backups
"""

from datetime import datetime, timezone
from sqlalchemy import delete, insert, select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.models.backup import ProductBackup
from app.models.product import ProductRow

# Columnas a incluir en el script (todas menos pk, que es autoincremental
# y podría chocar con filas existentes al restaurar)
COLUMNS = [c.name for c in ProductRow.__table__.columns if c.name != "pk"]

# Filas por sentencia INSERT: con miles de productos en un solo INSERT
# el script podría superar el max_allowed_packet de MySQL al restaurar
CHUNK_SIZE = 500

def create_backup(session: Session, supermarket: str) -> None:
    """Guarda un backup del catálogo ACTUAL del supermercado
    Se llama desde save_catalog, dentro de su misma transacción y antes
    del borrado: si algo falla, ni backup ni reemplazo (rollback total)"""
    rows = session.scalars(
        select(ProductRow).where(ProductRow.supermarket == supermarket)
    ).all()
    if not rows:
        return  # primer scraping: no hay nada que respaldar

    session.add(
        ProductBackup(
            supermarket=supermarket,
            created_at=datetime.now(timezone.utc),
            product_count=len(rows),
            sql_script=_build_script(supermarket, rows),
        )
    )
    _apply_retention(session, supermarket)


def list_backups() -> list[ProductBackup]:
    """Todos los backups, del más reciente al más antiguo (sin cargar
    el script, que puede pesar varios MB)"""
    with SessionLocal() as session:
        rows = session.execute(
            select(
                ProductBackup.pk,
                ProductBackup.supermarket,
                ProductBackup.created_at,
                ProductBackup.product_count,
            ).order_by(ProductBackup.created_at.desc())
        ).all()
    return rows


def get_backup(backup_id: int) -> ProductBackup | None:
    """Un backup completo, con su script, para descargarlo"""
    with SessionLocal() as session:
        return session.get(ProductBackup, backup_id)


def _build_script(supermarket: str, rows: list[ProductRow]) -> str:
    """Compone el script .sql que restaura el catálogo tal y como está
    SQLAlchemy renderiza los valores con literal_binds, que se encarga
    del escapado (comillas, acentos...) por nosotros"""
    fecha = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lineas = [
        f"-- Backup of {supermarket} generated on {fecha} ({len(rows)} products)",
        "-- Restore with: mysql supermarket_api < this_file.sql",
        "",
        f"DELETE FROM products WHERE supermarket = '{supermarket}';",
        "",
    ]

    # Dividimos en trozos para no superar el max_allowed_packet de MySQL
    for inicio in range(0, len(rows), CHUNK_SIZE):
        chunk = rows[inicio : inicio + CHUNK_SIZE]
        valores = [_row_to_dict(row) for row in chunk]
        sentencia = insert(ProductRow.__table__).values(valores)
        sql = str(
            sentencia.compile(
                bind=engine,
                compile_kwargs={"literal_binds": True},
            )
        )
        lineas.append(sql + ";")
        lineas.append("")

    return "\n".join(lineas)


def _row_to_dict(row: ProductRow) -> dict:
    """Convierte una fila en dict para el INSERT del script
    Las fechas se inyectan como literal SQL ya formateado (text) porque
    no todos los motores saben renderizar datetimes con literal_binds;
    'YYYY-MM-DD HH:MM:SS' lo aceptan tanto MySQL como SQLite"""
    valores = {}
    for columna in COLUMNS:
        valor = getattr(row, columna)
        if isinstance(valor, datetime):
            valor = text(f"'{valor.strftime('%Y-%m-%d %H:%M:%S')}'")
        valores[columna] = valor
    return valores


def _apply_retention(session: Session, supermarket: str) -> None:
    """Conserva solo los últimos N backups del supermercado"""
    antiguos = session.scalars(
        select(ProductBackup.pk)
        .where(ProductBackup.supermarket == supermarket)
        .order_by(ProductBackup.created_at.desc())
        .offset(settings.backups_keep)
    ).all()
    if antiguos:
        session.execute(delete(ProductBackup).where(ProductBackup.pk.in_(antiguos)))
