import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import pandas as pd
from openpyxl.styles import PatternFill, Font
from sqlalchemy import create_engine, text

from app.config import settings

KYIV_TZ = ZoneInfo("Europe/Kyiv")
YELLOW_FILL = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")


def build_report_sync(
    session_id: Optional[int] = None,
    store_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> str:
    """
    Генерація .xlsx звіту (синхронно, виконується в Celery-воркері).
    Повертає повний шлях до файлу.
    """
    sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    engine = create_engine(sync_url)

    filters = ["1=1"]
    params = {}

    if session_id:
        filters.append("ms.id = :session_id")
        params["session_id"] = session_id
    if store_id:
        filters.append("s.id = :store_id")
        params["store_id"] = store_id
    if date_from:
        filters.append("mr.created_at >= :date_from")
        params["date_from"] = date_from
    if date_to:
        filters.append("mr.created_at <= :date_to")
        params["date_to"] = date_to

    where_clause = " AND ".join(filters)

    query = text(f"""
        SELECT
            mr.created_at AT TIME ZONE 'Europe/Kyiv' AS "Дата/Час",
            u.full_name AS "Працівник",
            s.name AS "Магазин",
            p.article_id AS "Артикул",
            COALESCE(mr.custom_name, p.name) AS "Товар",
            mr.price AS "Ціна",
            CASE WHEN mr.is_promo THEN 'Акція' ELSE 'Звичайна' END AS "Тип ціни",
            mr.result_type AS "Тип запису"
        FROM monitoring_results mr
        JOIN monitoring_sessions ms ON mr.session_id = ms.id
        JOIN users u ON ms.user_id = u.id
        JOIN stores s ON ms.store_id = s.id
        LEFT JOIN products p ON mr.product_id = p.id
        WHERE {where_clause}
        ORDER BY mr.created_at
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)

    reports_path = settings.reports_path
    timestamp = datetime.now(KYIV_TZ).strftime("%Y%m%d_%H%M%S")
    filename = f"report_{session_id or 'custom'}_{timestamp}.xlsx"
    filepath = reports_path / filename

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Звіт")
        ws = writer.sheets["Звіт"]

        # Підсвічуємо новинки конкурента жовтим
        type_col_idx = df.columns.get_loc("Тип запису") + 1
        for row_idx, row_val in enumerate(df["Тип запису"], start=2):
            if row_val == "competitor_new":
                for col in ws.iter_cols(min_row=row_idx, max_row=row_idx,
                                        min_col=1, max_col=len(df.columns)):
                    for cell in col:
                        cell.fill = YELLOW_FILL
            elif row_val == "variant":
                name_col_idx = df.columns.get_loc("Товар") + 1
                ws.cell(row=row_idx, column=name_col_idx).font = Font(italic=True)

    return str(filepath)


def send_report_email(filepath: str, recipients: list[str], session_id: int):
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"Store Check — Звіт по сесії #{session_id}"

    msg.attach(MIMEText("Звіт цінового моніторингу у вкладенні.", "plain", "utf-8"))

    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={Path(filepath).name}",
        )
        msg.attach(part)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
