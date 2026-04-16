from sqlalchemy import Integer, ForeignKey, Boolean, String, Numeric, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class ResultType(str, enum.Enum):
    standard = "standard"
    variant = "variant"
    competitor_new = "competitor_new"


class MonitoringResult(Base):
    __tablename__ = "monitoring_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    product_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_promo: Mapped[bool] = mapped_column(Boolean, default=False)
    is_missing: Mapped[bool] = mapped_column(Boolean, default=False)
    custom_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    result_type: Mapped[ResultType] = mapped_column(SAEnum(ResultType), default=ResultType.standard)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
