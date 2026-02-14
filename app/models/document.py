from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DocumentBundle(SQLModel, table=True):
    """
    Logical grouping of related documents for an applicant
    (e.g., "Undergrad Application 2026").
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    applicant_id: int = Field(foreign_key="applicant.id", index=True)

    name: str
    status: str = Field(
        default="open", index=True
    )  # open, submitted, in_review, approved, rejected

    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    """
    Individual uploaded document stored in S3.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    bundle_id: int = Field(foreign_key="documentbundle.id", index=True)

    filename: str
    content_type: str
    s3_key: str = Field(index=True)
    size_bytes: Optional[int] = None

    scanned_status: str = Field(
        default="pending", index=True
    )  # pending, clean, infected, failed

    created_at: datetime = Field(default_factory=datetime.utcnow)

