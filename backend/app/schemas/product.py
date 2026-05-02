from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    article_id: str = Field(..., max_length=8, min_length=8)
    name: str = Field(..., max_length=500)
    category_id: int
    is_archived: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    article_id: Optional[str] = Field(None, max_length=8, min_length=8)
    name: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    is_archived: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
