from pydantic import BaseModel
from typing import Optional


class CategorySchema(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    level: str
    sort_order: int

    class Config:
        from_attributes = True


class ProductSchema(BaseModel):
    id: int
    article_id: str
    name: str
    weight_label: Optional[str] = None
    category_id: int

    class Config:
        from_attributes = True


class CatalogResponse(BaseModel):
    categories: list[CategorySchema]
    products: list[ProductSchema]
