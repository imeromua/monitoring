from pydantic import BaseModel
from datetime import datetime

class ReportFileResponse(BaseModel):
    filename: str
    size: int
    created_at: datetime
