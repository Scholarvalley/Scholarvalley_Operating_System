from __future__ import annotations

from typing import Any, Optional

from sqlmodel import Session

from app.models.audit import AuditLog


def log_event(
    session: Session,
    *,
    user_id: Optional[int],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Persist a simple audit log entry.
    """
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        extra_data=None if metadata is None else str(metadata),
        ip_address=ip_address,
    )
    session.add(log)
    session.commit()

