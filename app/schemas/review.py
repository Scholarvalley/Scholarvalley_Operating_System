from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    positive: bool = True
    feedback: Optional[str] = None


class ReviewRead(BaseModel):
    id: int
    applicant_id: int
    reviewer_user_id: int
    positive: bool
    feedback: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
