from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int
    role: str


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if not v or "@" not in v:
            raise ValueError("Invalid email")
        return v


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_not_empty(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if not v or "@" not in v:
            raise ValueError("Invalid email")
        return v

