from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ApplicantReview(SQLModel, table=True):
    """Review/rating of an applicant by a manager or root (positive/negative + feedback)."""

    id: Optional[int] = Field(default=None, primary_key=True)
    applicant_id: int = Field(foreign_key="applicant.id", index=True)
    reviewer_user_id: int = Field(foreign_key="user.id", index=True)
    positive: bool = True
    feedback: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
