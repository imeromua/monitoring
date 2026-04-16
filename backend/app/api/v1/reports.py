from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import os

from app.api.deps import require_admin
from app.models.user import User
from app.services.report_service import build_report_sync
from app.schemas.report import ReportRequest

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/export")
async def export_report(
    payload: ReportRequest,
    current_user: User = Depends(require_admin),
):
    filepath = build_report_sync(
        store_id=payload.store_id,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )
    filename = os.path.basename(filepath)
    return FileResponse(
        path=filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )
