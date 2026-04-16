from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionCreateRequest(BaseModel):
    store_id: int


class SessionResponse(BaseModel):
    id: int
    store_id: int
    status: str
    started_at: datetime

    class Config:
        from_attributes = True
