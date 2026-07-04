"""
Modelo de la tabla de backups de productos
"""

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class ProductBackup(Base):
    """Backup del catálogo de un supermercado, generado automáticamente
    antes de cada reemplazo en save_catalog"""

    __tablename__ = "product_backups"

    pk: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # De qué supermercado es el backup
    supermarket: Mapped[str] = mapped_column(
        String(32),
        index=True,
    )

    # Cuándo se hizo
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    # Cuántos productos contenía el catálogo en ese momento
    product_count: Mapped[int] = mapped_column(
        Integer,
    )

    # El script .sql completo que restaura el catálogo
    # MEDIUMTEXT en MySQL (hasta 16 MB); en SQLite, Text normal
    sql_script: Mapped[str] = mapped_column(
        Text().with_variant(MEDIUMTEXT(), "mysql"),
    )
