"""
Esquemas de los backups de productos
"""

from datetime import datetime
from pydantic import BaseModel, Field

class BackupInfo(BaseModel):
    """Ficha de un backup (sin el script, que puede pesar varios MB)
    El script se descarga en GET /backups/{id}/download"""

    id: int = Field(
        description="Backup ID",
    )
    supermarket: str = Field(
        description="Supermarket name",
    )
    created_at: datetime = Field(
        description="When it was generated",
    )
    product_count: int = Field(
        description="Products that were in the catalog",
    )
