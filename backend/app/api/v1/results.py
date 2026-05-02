from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.api.deps import get_current_user
from app.models.session import MonitoringSession, SessionStatus
from app.models.result import MonitoringResult
from app.models.stats import StoreProductStats
from app.models.user import User
from app.schemas.result import ResultCreateRequest, ResultResponse

router = APIRouter(prefix="/sessions", tags=["results"])

MISSING_THRESHOLD = 3


@router.post("/{session_id}/results", response_model=ResultResponse)
async def add_result(
    session_id: int,
    payload: ResultCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    async with db.begin():
        # SELECT ... FOR UPDATE всередині транзакції для уникнення race condition
        sess = (await db.execute(
            select(MonitoringSession)
            .where(
                MonitoringSession.id == session_id,
                MonitoringSession.user_id == current_user.id,
                MonitoringSession.status == SessionStatus.in_progress,
            )
            .with_for_update()
        )).scalar_one_or_none()

        if not sess:
            raise HTTPException(status_code=404, detail="Активну сесію не знайдено")

        result = MonitoringResult(
            session_id=session_id,
            product_id=payload.product_id,
            price=payload.price,
            is_promo=payload.is_promo,
            is_missing=payload.is_missing,
            custom_name=payload.custom_name,
            result_type=payload.result_type,
        )
        db.add(result)

        # Оновлення лічильника Smart Hide
        if payload.product_id:
            stats = (await db.execute(
                select(StoreProductStats).where(
                    StoreProductStats.store_id == sess.store_id,
                    StoreProductStats.product_id == payload.product_id,
                )
            )).scalar_one_or_none()

            if not stats:
                stats = StoreProductStats(
                    store_id=sess.store_id,
                    product_id=payload.product_id,
                )
                db.add(stats)

            if payload.is_missing:
                stats.consecutive_missing_count += 1
                if stats.consecutive_missing_count >= MISSING_THRESHOLD:
                    stats.is_hidden = True
            else:
                stats.consecutive_missing_count = 0
                stats.is_hidden = False

    await db.refresh(result)
    return result
