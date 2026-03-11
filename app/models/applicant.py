from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Applicant(SQLModel, table=True):
    """
    Represents a client applicant in the system.

    Links back to the account User (owner) and optionally to a manager User.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Owner of this applicant record (client account)
    account_user_id: int = Field(foreign_key="user.id", index=True)

    first_name: str
    last_name: str

    latest_education: Optional[str] = Field(default=None)  # e.g. "Bachelor of Science, XYZ University"

    # Profile and service interest
    country_of_residence: Optional[str] = Field(default=None)
    study_destination: Optional[str] = Field(default=None)  # "USA" or "Canada"
    level_of_study: Optional[str] = Field(default=None)  # freshman, continuing_undergrad, graduate
    annual_budget: Optional[str] = Field(default=None)
    income_source: Optional[str] = Field(default=None)
    service_interest: Optional[str] = Field(default=None)

    status: str = Field(
        default="draft", index=True
    )  # draft, in_review, accepted, rejected, archived

    # Assigned manager handling this applicant
    assigned_manager_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

