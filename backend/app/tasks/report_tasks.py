from app.celery_app import celery
from app.services.report_service import build_report_sync, send_report_email
from app.config import settings


@celery.task(
    name="app.tasks.report_tasks.generate_and_send_report",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_and_send_report(self, session_id: int):
    """
    Фонова Celery-задача:
    1. Генерує .xlsx звіт по session_id
    2. Відправляє email аналітикам
    При помилці автоматично повторює 3 рази з інтервалом 60 сек.
    """
    try:
        filepath = build_report_sync(session_id=session_id)
        send_report_email(
            filepath=filepath,
            recipients=settings.report_recipients_list,
            session_id=session_id,
        )
        return f"Report for session {session_id} sent successfully"
    except Exception as exc:
        raise self.retry(exc=exc)
