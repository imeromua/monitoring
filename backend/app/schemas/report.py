from pydantic import BaseModel
from datetime import date
from typing import Optional


class ReportRequest(BaseModel):
    store_id: Optional[int] = None
    date_from: date
    date_to: date
