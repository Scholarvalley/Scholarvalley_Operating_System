from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApplicantCreate(BaseModel):
    first_name: str
    last_name: str
    latest_education: Optional[str] = None
    service_interest: Optional[str] = None
    country_of_residence: Optional[str] = None
    study_destination: Optional[str] = None
    level_of_study: Optional[str] = None
    annual_budget: Optional[str] = None
    income_source: Optional[str] = None


class ApplicantRead(BaseModel):
    id: int
    account_user_id: int
    first_name: str
    last_name: str
    latest_education: Optional[str]
    service_interest: Optional[str]
    country_of_residence: Optional[str]
    study_destination: Optional[str]
    level_of_study: Optional[str]
    annual_budget: Optional[str]
    income_source: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicantCreateResponse(BaseModel):
    applicant_id: int
    bundle_id: int
    first_name: str
    last_name: str
    status: str


class ApplicantListEntry(BaseModel):
    """Applicant row for dashboard list (includes owner email for managers)."""
    id: int
    first_name: str
    last_name: str
    latest_education: Optional[str]
    status: str
    created_at: datetime
    owner_email: Optional[str] = None

    class Config:
        from_attributes = True
