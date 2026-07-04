"""
Capa de modelos (ORM)
"""

from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.schemas.product import Product

class ProductRow(Base):
    """Tabla de productos. Cada scraping reemplaza las filas de su supermercado"""

    __tablename__ = "products"

    # Clave primaria propia de la tabla (autoincremental)
    pk: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Identificador del producto en su supermercado
    external_id: Mapped[str] = mapped_column(
        String(64),
    )

    # Con índice ya que casi todas las consultas filtran por supermercado
    supermarket: Mapped[str] = mapped_column(
        String(32),
        index=True,
    )

    # Con índice ya que es el campo principal de búsqueda
    name: Mapped[str] = mapped_column(
        String(512),
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    brand: Mapped[str | None] = mapped_column(
        String(255),
    )

    # Precio actual estimado en EUR
    price: Mapped[float | None] = mapped_column(
        Float,
    )

    # Precio por unidad de referencia (por Kg, por L...)
    price_per_unit: Mapped[float | None] = mapped_column(
        Float,
    )

    unit: Mapped[str | None] = mapped_column(
        String(64),
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
    )

    category: Mapped[str | None] = mapped_column(
        String(255),
    )

    # Con índice ya que permite cruzar el mismo producto entre supermercados
    ean: Mapped[str | None] = mapped_column(
        String(32),
        index=True,
    )

    url: Mapped[str | None] = mapped_column(
        Text,
    )

    # Cuándo se scrapeó esta fila
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime,
    )

    def to_schema(self) -> Product:
        """Convierte la fila de BBDD al esquema que devuelve la API"""
        return Product(
            id=self.external_id,
            supermarket=self.supermarket,
            name=self.name,
            description=self.description,
            brand=self.brand,
            price=self.price,
            price_per_unit=self.price_per_unit,
            unit=self.unit,
            image_url=self.image_url,
            category=self.category,
            ean=self.ean,
            url=self.url,
        )
