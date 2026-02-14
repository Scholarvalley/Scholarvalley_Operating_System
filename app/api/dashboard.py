from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlmodel import Session

from app.api.auth import require_role
from app.db.session import get_session
from app.models.applicant import Applicant
from app.models.payment import Payment
from app.models.task import Task
from app.models.user import User


router = APIRouter()


@router.get("/summary")
def dashboard_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("manager", "root")),
):
    accepted_clients = session.exec(
        select(func.count()).select_from(Applicant).where(Applicant.status == "accepted")
    ).one()

    pending_tasks = session.exec(
        select(func.count()).select_from(Task).where(Task.status == "pending")
    ).one()

    total_revenue_cents = session.exec(
        select(func.coalesce(func.sum(Payment.amount_cents), 0))
        .select_from(Payment)
        .where(Payment.status == "succeeded")
    ).one()

    return {
        "accepted_clients": accepted_clients[0],
        "pending_tasks": pending_tasks[0],
        "total_revenue_cents": total_revenue_cents[0],
    }

