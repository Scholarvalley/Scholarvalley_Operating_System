from __future__ import annotations

import json
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.auth import get_current_user
from app.db.session import get_session
from app.models.eligibility import EligibilityResult
from app.models.user import User
from app.schemas.eligibility import EligibilityInput, EligibilityOutput


router = APIRouter()


@router.post("/check", response_model=EligibilityOutput)
def check_eligibility(
    payload: EligibilityInput,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Simple rule-based eligibility engine, extendable to ML later.
    """
    recommendations: list[str]
    is_eligible: bool

    if payload.gpa >= 3.5 and payload.toefl >= 90:
        is_eligible = True
        recommendations = ["Top-tier programs", "Scholarship-focused options"]
    elif payload.gpa >= 3.0 and payload.toefl >= 80:
        is_eligible = True
        recommendations = ["Solid programs", "Consider mid-tier schools"]
    else:
        is_eligible = False
        recommendations = ["Foundational programs", "Language or academic prep first"]

    created_at = datetime.utcnow()

    result_record = EligibilityResult(
        applicant_id=payload.applicant_id,
        input_payload=json.dumps(payload.model_dump()),
        result_payload=json.dumps(
            {
                "is_eligible": is_eligible,
                "recommendations": recommendations,
                "evaluated_by_user_id": current_user.id,
                "created_at": created_at.isoformat(),
            }
        ),
    )
    session.add(result_record)
    session.commit()

    return EligibilityOutput(
        applicant_id=payload.applicant_id,
        is_eligible=is_eligible,
        recommendations=recommendations,
        created_at=created_at,
    )

