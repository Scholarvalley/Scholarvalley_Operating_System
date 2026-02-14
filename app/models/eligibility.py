from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EligibilityResult(SQLModel, table=True):
    """
    Stores the outcome of an eligibility check for an applicant.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    applicant_id: int = Field(foreign_key="applicant.id", index=True)

    # Simple stringified JSON payload of the inputs and result
    input_payload: str
    result_payload: str

    created_at: datetime = Field(default_factory=datetime.utcnow)

