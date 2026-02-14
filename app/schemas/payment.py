from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PaymentCreate(BaseModel):
    amount_cents: int
    currency: str = "usd"
    applicant_id: Optional[int] = None
    success_url: str
    cancel_url: str


class PaymentRead(BaseModel):
    id: int
    amount_cents: int
    currency: str
    status: str
    created_at: datetime
    applicant_id: Optional[int] = None

    class Config:
        from_attributes = True

