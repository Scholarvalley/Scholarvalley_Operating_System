from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.auth import get_current_user, require_role
from app.db.session import get_session
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead


router = APIRouter()


@router.post("/", response_model=TaskRead)
def create_task(
    payload: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("manager", "root")),
):
    assignee_id = payload.assignee_id or current_user.id

    task = Task(
        applicant_id=payload.applicant_id,
        assignee_id=assignee_id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    assignee_id: Optional[int] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    applicant_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = select(Task)

    if applicant_id is not None:
        query = query.where(Task.applicant_id == applicant_id)

    if assignee_id is not None:
        query = query.where(Task.assignee_id == assignee_id)
    else:
        # Default: show tasks assigned to current user
        query = query.where(Task.assignee_id == current_user.id)

    if status_filter:
        query = query.where(Task.status == status_filter)

    offset = (page - 1) * limit
    results = session.exec(query.offset(offset).limit(limit)).all()
    return results


@router.patch("/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    new_status: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if current_user.role not in ("manager", "root") and task.assignee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    task.status = new_status
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

