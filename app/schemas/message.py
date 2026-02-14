from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageCreate(BaseModel):
    applicant_id: Optional[int] = None
    recipient_id: Optional[int] = None
    body: str


class MessageRead(BaseModel):
    id: int
    applicant_id: Optional[int]
    sender_id: int
    recipient_id: Optional[int]
    body: str
    created_at: datetime
    read_at: Optional[datetime]

    class Config:
        from_attributes = True

