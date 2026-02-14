from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """
    Internal message related to an applicant (client <-> manager).
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    applicant_id: Optional[int] = Field(
        default=None, foreign_key="applicant.id", index=True
    )

    sender_id: int = Field(foreign_key="user.id", index=True)
    recipient_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )

    body: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = Field(default=None)

