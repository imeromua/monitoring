from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery(
    "store_check",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.report_tasks",
        "app.tasks.maintenance",
    ],
)

celery.conf.timezone = "Europe/Kyiv"
celery.conf.enable_utc = True

celery.conf.beat_schedule = {
    "cleanup-old-reports": {
        "task": "app.tasks.maintenance.cleanup_old_reports",
        "schedule": crontab(hour=3, minute=0),  # щодня о 03:00 Kyiv
    },
}
