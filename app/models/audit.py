from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    """
    Immutable audit log for key security and business events.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", index=True
    )

    action: str = Field(index=True)  # e.g., "login", "file_upload", "role_change"
    resource_type: Optional[str] = Field(default=None, index=True)
    resource_id: Optional[str] = Field(default=None, index=True)

    # Simple stringified JSON (avoid name 'metadata' - reserved by SQLAlchemy)
    extra_data: Optional[str] = Field(default=None)

    ip_address: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

