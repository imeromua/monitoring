from pydantic import BaseModel, field_validator
from typing import Optional
from decimal import Decimal


class ResultCreateRequest(BaseModel):
    product_id: Optional[int] = None
    price: Optional[Decimal] = None
    is_promo: bool = False
    is_missing: bool = False
    custom_name: Optional[str] = None
    result_type: str = "standard"

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Ціна не може бути від'ємною")
            if v > 100_000:
                raise ValueError("Ціна перевищує допустиме значення")
        return v


class ResultResponse(BaseModel):
    id: int
    product_id: Optional[int]
    price: Optional[Decimal]
    is_promo: bool
    is_missing: bool
    result_type: str

    class Config:
        from_attributes = True
