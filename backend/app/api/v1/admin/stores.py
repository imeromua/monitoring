import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.api.deps import require_admin
from app.models.store import Store
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/admin/stores", tags=["admin"])


@router.post("")
async def create_store(
    name: str,
    address: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    store = Store(name=name, address=address)
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return {"id": store.id, "name": store.name}


@router.patch("/{store_id}/archive")
async def archive_store(
    store_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не знайдено")
    store.is_active = False
    await db.commit()
    return {"status": "archived", "store_id": store_id}


ALLOWED_LOGO_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2 MB


@router.post("/{store_id}/logo")
async def upload_store_logo(
    store_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Магазин не знайдено")

    if file.content_type not in ALLOWED_LOGO_TYPES:
        raise HTTPException(status_code=400, detail="Дозволено лише PNG, JPG або WebP")

    content = await file.read()
    if len(content) > MAX_LOGO_SIZE:
        raise HTTPException(status_code=400, detail="Файл занадто великий (макс. 2 МБ)")

    # Видалити старе лого якщо є
    if store.logo_url:
        old_filename = store.logo_url.split("/")[-1]
        old_path = os.path.join(str(settings.stores_logos_path), old_filename)
        if os.path.isfile(old_path):
            os.remove(old_path)

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"store_{store_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(str(settings.stores_logos_path), filename)

    with open(filepath, "wb") as f:
        f.write(content)

    store.logo_url = f"/api/v1/static/store-logos/{filename}"
    await db.commit()

    return {"logo_url": store.logo_url}
