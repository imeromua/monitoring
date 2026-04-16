from sqlalchemy import String, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base


class CategoryLevel(str, enum.Enum):
    division = "division"       # Відділ
    department = "department"   # Департамент
    group = "group"             # Група


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    level: Mapped[CategoryLevel] = mapped_column(SAEnum(CategoryLevel), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    children = relationship("Category", backref="parent", remote_side="Category.id")
