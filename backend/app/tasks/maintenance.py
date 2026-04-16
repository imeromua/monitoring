import time
from pathlib import Path
from app.celery_app import celery
from app.config import settings


@celery.task(name="app.tasks.maintenance.cleanup_old_reports")
def cleanup_old_reports():
    """
    Видаляє .xlsx файли старіші за REPORT_TTL_HOURS з папки звітів.
    Запускається автоматично через Celery Beat о 03:00.
    """
    reports_dir = Path(settings.REPORTS_DIR)
    if not reports_dir.exists():
        return "Reports directory does not exist"

    ttl_seconds = settings.REPORT_TTL_HOURS * 3600
    now = time.time()
    removed = 0

    for file in reports_dir.glob("*.xlsx"):
        if (now - file.stat().st_mtime) > ttl_seconds:
            file.unlink()
            removed += 1

    return f"Cleaned up {removed} report(s)"
