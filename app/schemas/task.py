from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    applicant_id: Optional[int] = None
    assignee_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None


class TaskRead(BaseModel):
    id: int
    applicant_id: Optional[int]
    assignee_id: Optional[int]
    title: str
    description: Optional[str]
    status: str
    due_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

