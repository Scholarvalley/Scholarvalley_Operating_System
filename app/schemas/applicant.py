from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApplicantCreate(BaseModel):
    first_name: str
    last_name: str
    latest_education: Optional[str] = None


class ApplicantRead(BaseModel):
    id: int
    account_user_id: int
    first_name: str
    last_name: str
    latest_education: Optional[str]
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
