"""
Punto de configuración de la aplicación
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Configuración de la aplicación
class Settings(BaseSettings):
    # Vacío = SQLite local (desarrollo)
    #  Para MySQL, en el .env:
    # SUPERMARKET_API_DATABASE_URL=mysql+pymysql://usuario:password@host:3306/supermarket_api?charset=utf8mb4
    database_url: str = ""

    data_dir: Path = Path(__file__).resolve().parents[2] / "data" # Directorio de datos (por defecto, ./data)

    # Orígenes permitidos para CORS. Se configura en el .env (formato JSON):
    # SUPERMARKET_API_CORS_ORIGINS=["https://dev.supermarket-api.online"]
    # Vacío = ningún frontend externo puede llamar a la API desde el navegador.
    cors_origins: list[str] = []

    backups_keep: int = 5 # Backups a conservar por supermercado (los más antiguos se borran solos)
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" # User Agent es importante para que los scrapers no sean bloqueados por los supermercados

    # Configuración de la clase interna Config para pydantic-settings
    class Config:
        env_prefix = "SUPERMARKET_API_"
        env_file = ".env"

# Instancia de la configuración
settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True) # Crea el directorio de datos si no existe
if not settings.database_url:
    settings.database_url = f"sqlite:///{settings.data_dir / 'products.db'}" # Si no hay URL de base de datos, usa SQLite local en ./data/products.db
