from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.auth import get_current_user, require_role
from app.db.session import get_session
from app.models.applicant import Applicant
from app.models.document import DocumentBundle
from app.models.review import ApplicantReview
from app.models.user import User
from app.schemas.applicant import (
    ApplicantCreate,
    ApplicantCreateResponse,
    ApplicantListEntry,
    ApplicantRead,
)
from app.schemas.review import ReviewCreate, ReviewRead


router = APIRouter()


@router.post("/", response_model=ApplicantCreateResponse)
def create_applicant(
    payload: ApplicantCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create an applicant and a default document bundle for registration uploads."""
    applicant = Applicant(
        account_user_id=current_user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        latest_education=payload.latest_education,
        service_interest=payload.service_interest,
        country_of_residence=payload.country_of_residence,
        study_destination=payload.study_destination,
        level_of_study=payload.level_of_study,
        annual_budget=payload.annual_budget,
        income_source=payload.income_source,
        status="draft",
    )
    session.add(applicant)
    session.commit()
    session.refresh(applicant)

    bundle = DocumentBundle(
        applicant_id=applicant.id,
        name="Registration documents",
        status="open",
    )
    session.add(bundle)
    session.commit()
    session.refresh(bundle)

    return ApplicantCreateResponse(
        applicant_id=applicant.id,
        bundle_id=bundle.id,
        first_name=applicant.first_name,
        last_name=applicant.last_name,
        status=applicant.status,
    )


@router.get("/", response_model=List[ApplicantListEntry])
def list_applicants(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """List applicants. Clients see only their own; managers and root see all with owner email."""
    base = select(Applicant)
    if current_user.role == "client":
        base = base.where(Applicant.account_user_id == current_user.id)
    base = base.order_by(Applicant.created_at.desc())
    offset = (page - 1) * limit
    rows = session.exec(base.offset(offset).limit(limit)).all()
    out = []
    for app in rows:
        owner = session.get(User, app.account_user_id)
        out.append(
            ApplicantListEntry(
                id=app.id,
                first_name=app.first_name,
                last_name=app.last_name,
                latest_education=app.latest_education,
                status=app.status,
                created_at=app.created_at,
                owner_email=owner.email if owner and current_user.role in ("manager", "root") else None,
            )
        )
    return out


@router.get("/{applicant_id}", response_model=ApplicantRead)
def get_applicant(
    applicant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get one applicant profile. Clients can only access their own."""
    applicant = session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    if current_user.role == "client" and applicant.account_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return applicant


@router.get("/{applicant_id}/bundle")
def get_applicant_bundle(
    applicant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return the first (registration) bundle for an applicant. Clients only own; manager/root see any."""
    applicant = session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    if current_user.role == "client" and applicant.account_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    bundle = session.exec(
        select(DocumentBundle).where(DocumentBundle.applicant_id == applicant_id)
    ).first()
    if not bundle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No bundle found")
    return {"applicant_id": applicant_id, "bundle_id": bundle.id}


@router.post("/{applicant_id}/review", response_model=ReviewRead)
def submit_applicant_review(
    applicant_id: int,
    payload: ReviewCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role("manager", "root")),
):
    """Submit a review (positive/negative + optional feedback) for an applicant. Manager/root only."""
    applicant = session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    review = ApplicantReview(
        applicant_id=applicant_id,
        reviewer_user_id=current_user.id,
        positive=payload.positive,
        feedback=payload.feedback,
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.get("/{applicant_id}/reviews", response_model=List[ReviewRead])
def list_applicant_reviews(
    applicant_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List reviews for an applicant. Caller must be able to access the applicant."""
    applicant = session.get(Applicant, applicant_id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")
    if current_user.role == "client" and applicant.account_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    reviews = session.exec(
        select(ApplicantReview).where(ApplicantReview.applicant_id == applicant_id).order_by(ApplicantReview.created_at.desc())
    ).all()
    return list(reviews)
