"""
Router de backups
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.schemas.backup import BackupInfo
from app.services import backup_service

router = APIRouter(prefix="/backups", tags=["backups"]) # Declaración del router

# GET de la lista de backups (sin el script, que puede pesar varios MB)
@router.get("", response_model=list[BackupInfo])
def backups() -> list[BackupInfo]:
    return backup_service.get_backups()

# GET de descarga: devuelve el script como fichero .sql adjunto
@router.get("/{backup_id}/download")
def download_backup(backup_id: int) -> Response:
    resultado = backup_service.get_backup_download(backup_id)
    if resultado is None:
        raise HTTPException(404, f"Backup not found: {backup_id}")
    filename, script = resultado
    # Content-Disposition: attachment hace que el navegador lo descargue
    # como fichero en vez de mostrarlo
    return Response(
        content=script,
        media_type="application/sql",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
