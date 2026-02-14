from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.db.session import get_session
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageRead


router = APIRouter()


@router.post("/", response_model=MessageRead)
def create_message(
    payload: MessageCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    message = Message(
        applicant_id=payload.applicant_id,
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        body=payload.body,
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@router.get("/", response_model=List[MessageRead])
def list_messages(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    applicant_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = select(Message)

    if applicant_id is not None:
        query = query.where(Message.applicant_id == applicant_id)
    else:
        # Show messages either sent or received by current user
        query = query.where(
            (Message.sender_id == current_user.id)
            | (Message.recipient_id == current_user.id)
        )

    offset = (page - 1) * limit
    results = session.exec(query.offset(offset).limit(limit)).all()
    return results


@router.post("/{message_id}/read", response_model=MessageRead)
def mark_read(
    message_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    if message.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    from datetime import datetime

    message.read_at = datetime.utcnow()
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

