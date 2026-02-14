from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MLTrainingConsent(SQLModel, table=True):
    """
    Records explicit opt-in for using data in ML training.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )
    applicant_id: Optional[int] = Field(
        default=None, foreign_key="applicant.id", index=True
    )

    consent_given: bool = Field(default=True)
    version: str = Field(default="v1")

    consented_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)

