from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProductBase(BaseModel):
    article_id: str = Field(..., max_length=8, min_length=8)
    name: str = Field(..., max_length=500)
    category_id: int
    is_archived: bool = False

    @field_validator("article_id")
    @classmethod
    def validate_article(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Артикул повинен містити тільки цифри")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    article_id: Optional[str] = Field(None, max_length=8, min_length=8)
    name: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    is_archived: Optional[bool] = None

    @field_validator("article_id", mode="before")
    @classmethod
    def validate_article(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.isdigit():
            raise ValueError("Артикул повинен містити тільки цифри")
        return v


class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
