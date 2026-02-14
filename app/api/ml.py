from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.db.session import get_session
from app.models.consent import MLTrainingConsent
from app.models.user import User
from app.schemas.ml import (
    MLConsentUpdate,
    MLRecommendationRequest,
    MLRecommendationResponse,
)


router = APIRouter()


@router.post("/consent")
def update_ml_consent(
    payload: MLConsentUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Record or update ML training consent.
    """
    stmt = select(MLTrainingConsent).where(
        MLTrainingConsent.user_id == current_user.id,
        MLTrainingConsent.applicant_id == payload.applicant_id,
        MLTrainingConsent.version == payload.version,
    )
    existing = session.exec(stmt).first()

    if existing:
        existing.consent_given = payload.consent_given
        if not payload.consent_given:
            from datetime import datetime

            existing.revoked_at = datetime.utcnow()
        session.add(existing)
    else:
        consent = MLTrainingConsent(
            user_id=current_user.id,
            applicant_id=payload.applicant_id,
            consent_given=payload.consent_given,
            version=payload.version,
        )
        session.add(consent)

    session.commit()
    return {"ok": True}


@router.post("/recommendation", response_model=MLRecommendationResponse)
def ml_recommendation(
    payload: MLRecommendationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Stub endpoint for ML-based recommendations.

    In a later phase this will:
    - check MLTrainingConsent
    - call a SageMaker/Deepseek endpoint
    - return model-generated recommendations
    """
    stmt = select(MLTrainingConsent).where(
        MLTrainingConsent.user_id == current_user.id,
        MLTrainingConsent.applicant_id == payload.applicant_id,
        MLTrainingConsent.consent_given.is_(True),
    )
    consent = session.exec(stmt).first()
    if not consent:
        return MLRecommendationResponse(
            applicant_id=payload.applicant_id,
            recommendation="No ML recommendation available (consent not granted).",
            model_version="none",
        )

    # Placeholder recommendation
    return MLRecommendationResponse(
        applicant_id=payload.applicant_id,
        recommendation="ML recommendation service is not yet implemented. This will call Deepseek/SageMaker.",
        model_version="planned-v1",
    )

