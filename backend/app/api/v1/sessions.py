from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.session import MonitoringSession, SessionStatus
from app.models.user import User
from app.schemas.session import SessionCreateRequest, SessionResponse
from app.tasks.report_tasks import generate_and_send_report

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = MonitoringSession(
        user_id=current_user.id,
        store_id=payload.store_id,
        status=SessionStatus.in_progress,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.patch("/{session_id}/complete")
async def complete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MonitoringSession).where(
            MonitoringSession.id == session_id,
            MonitoringSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")

    session.status = SessionStatus.completed
    session.finished_at = datetime.now(timezone.utc)
    await db.commit()

    # Запуск фонової Celery-задачі
    generate_and_send_report.delay(session_id)

    return {"status": "completed", "session_id": session_id}
