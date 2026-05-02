import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List

from app.api.deps import require_admin
from app.models.user import User
from app.config import settings
from app.schemas.report_archive import ReportFileResponse

router = APIRouter(prefix="/admin/reports/archive", tags=["admin"])


@router.get("", response_model=List[ReportFileResponse])
async def list_reports(current_user: User = Depends(require_admin)):
    """Повертає список всіх збережених звітів у теці REPORTS_DIR"""
    reports_dir = str(settings.reports_path)  # автостворює папку якщо не існує

    files = []
    for entry in os.scandir(reports_dir):
        if entry.is_file() and entry.name.endswith(".xlsx"):
            stat = entry.stat()
            files.append(
                ReportFileResponse(
                    filename=entry.name,
                    size=stat.st_size,
                    created_at=datetime.fromtimestamp(stat.st_ctime),
                )
            )

    files.sort(key=lambda x: x.created_at, reverse=True)
    return files


@router.get("/{filename}")
async def download_report(
    filename: str,
    current_user: User = Depends(require_admin),
):
    """Завантажує файл звіту за його назвою"""
    safe_base = os.path.realpath(str(settings.reports_path))
    filepath = os.path.join(safe_base, filename)
    real_path = os.path.realpath(filepath)

    if not real_path.startswith(safe_base) or not os.path.isfile(real_path):
        raise HTTPException(status_code=404, detail="Файл не знайдено або доступ заборонено")

    return FileResponse(
        path=real_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
