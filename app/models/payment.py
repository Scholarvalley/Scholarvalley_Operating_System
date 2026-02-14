from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Payment(SQLModel, table=True):
    """
    Stripe payment record associated with an applicant or account.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    applicant_id: Optional[int] = Field(
        default=None, foreign_key="applicant.id", index=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )

    amount_cents: int
    currency: str = Field(default="usd")

    stripe_payment_intent_id: Optional[str] = Field(default=None, index=True)
    stripe_checkout_session_id: Optional[str] = Field(default=None, index=True)

    status: str = Field(
        default="created", index=True
    )  # created, pending, succeeded, failed, refunded

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

