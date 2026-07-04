"""
Conexión a la base de datos (SQLAlchemy)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# pool_pre_ping y pool_recycle evitan el error "MySQL server has gone away"
# cuando la API lleva horas sin recibir peticiones.
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=3600)

# Crea una sesión de base de datos (para cada petición) que se cierra automáticamente al terminar la petición
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos de SQLAlchemy"""

def init_db() -> None:
    """Crea las tablas que falten. Se llama una vez, al arrancar la API."""
    from app.models import backup, product  # noqa: F401  (importa para registrar las tablas)
    Base.metadata.create_all(engine) # Crea las tablas que falten en la base de datos
