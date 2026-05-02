import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.session import MonitoringSession, SessionStatus
from app.models.user import User
from app.schemas.session import SessionCreateRequest, SessionResponse
from app.config import settings
from app.services.report_service import build_report_sync, send_report_email

logger = logging.getLogger(__name__)

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


def _sync_generate_and_send(session_id: int):
    """
    Синхронна версія задачі — виконується у BackgroundTasks FastAPI
    якщо Celery недоступний або недоданий.
    """
    try:
        filepath = build_report_sync(session_id=session_id)
        send_report_email(
            filepath=filepath,
            recipients=settings.report_recipients_list,
            session_id=session_id,
        )
        logger.info("Report for session %d sent via BackgroundTasks", session_id)
    except Exception:
        logger.exception("Failed to generate/send report for session %d", session_id)


@router.patch("/{session_id}/complete")
async def complete_session(
    session_id: int,
    background_tasks: BackgroundTasks,
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

    # Спробуємо запустити через Celery (якщо воркер запущено)
    # При будь-якій помилці — запускаємо у фоні FastAPI (BackgroundTasks)
    celery_dispatched = False
    try:
        from app.tasks.report_tasks import generate_and_send_report
        generate_and_send_report.delay(session_id)
        celery_dispatched = True
        logger.info("Report task dispatched to Celery for session %d", session_id)
    except Exception:
        logger.warning(
            "Celery unavailable for session %d — falling back to BackgroundTasks",
            session_id,
        )

    if not celery_dispatched:
        background_tasks.add_task(_sync_generate_and_send, session_id)

    return {"status": "completed", "session_id": session_id}
