"""
Servicio de backups: listado y descarga
"""

from app.repositories import backup_repository
from app.schemas.backup import BackupInfo

def get_backups() -> list[BackupInfo]:
    """Fichas de todos los backups, del más reciente al más antiguo"""
    return [
        BackupInfo(
            id=row.pk,
            supermarket=row.supermarket,
            created_at=row.created_at,
            product_count=row.product_count,
        )
        for row in backup_repository.list_backups()
    ]


def get_backup_download(backup_id: int) -> tuple[str, str] | None:
    """Devuelve (nombre de fichero, script SQL) o None si no existe"""
    backup = backup_repository.get_backup(backup_id)
    if backup is None:
        return None
    fecha = backup.created_at.strftime("%Y-%m-%d_%H%M%S")
    filename = f"backup_{backup.supermarket}_{fecha}.sql"
    return filename, backup.sql_script
