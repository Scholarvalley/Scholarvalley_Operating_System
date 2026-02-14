from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    full_name: Optional[str] = None
    hashed_password: str
    role: str = Field(default="client", index=True)  # root, manager, client
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

