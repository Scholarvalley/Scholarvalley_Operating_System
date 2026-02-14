from datetime import datetime
from typing import List

from pydantic import BaseModel


class EligibilityInput(BaseModel):
    applicant_id: int
    gpa: float
    toefl: int
    notes: str | None = None


class EligibilityOutput(BaseModel):
    applicant_id: int
    is_eligible: bool
    recommendations: List[str]
    created_at: datetime

