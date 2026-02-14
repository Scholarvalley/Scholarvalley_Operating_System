from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Workflow task assigned to a manager or client (e.g., "Upload transcript").
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    applicant_id: Optional[int] = Field(
        default=None, foreign_key="applicant.id", index=True
    )

    assignee_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )

    title: str
    description: Optional[str] = None

    status: str = Field(
        default="pending", index=True
    )  # pending, in_progress, completed, cancelled

    due_at: Optional[datetime] = Field(default=None, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

