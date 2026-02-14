from __future__ import annotations

from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.document import Document, DocumentBundle
from app.models.user import User
from app.services.audit import log_event


router = APIRouter()
settings = get_settings()
s3_client = boto3.client("s3", region_name=settings.aws_region)


def _check_bundle_access(session: Session, bundle_id: int, user: User) -> DocumentBundle:
    bundle = session.get(DocumentBundle, bundle_id)
    if not bundle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")
    from app.models.applicant import Applicant
    applicant = session.get(Applicant, bundle.applicant_id)
    if not applicant or applicant.account_user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found")
    return bundle


@router.post("/bundles/{bundle_id}/documents/initiate")
def initiate_bundle_upload(
    bundle_id: int,
    filename: str,
    content_type: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a Document record and return a presigned URL for uploading (e.g. transcript or degree)."""
    bundle = _check_bundle_access(session, bundle_id, current_user)
    key = f"documents/{bundle_id}/{uuid4()}/{filename}"

    doc = Document(
        bundle_id=bundle_id,
        filename=filename,
        content_type=content_type,
        s3_key=key,
        scanned_status="pending",
    )
    session.add(doc)
    session.commit()
    session.refresh(doc)

    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.aws_s3_bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=900,
        )
    except ClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate presigned URL",
        ) from exc

    log_event(
        session=session,
        user_id=current_user.id,
        action="document_upload_initiated",
        resource_type="document",
        resource_id=str(doc.id),
        metadata={"bundle_id": bundle_id, "filename": filename},
        ip_address=request.client.host if request.client else None,
    )

    return {"upload_url": url, "key": key, "document_id": doc.id, "content_type": content_type}


class DocumentCompleteBody(BaseModel):
    key: str


@router.post("/documents/{document_id}/complete")
def complete_document_upload(
    document_id: int,
    body: DocumentCompleteBody,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Confirm the file was uploaded to S3 and update the document record."""
    key = body.key
    doc = session.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc.s3_key != key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Key does not match document")
    bundle = _check_bundle_access(session, doc.bundle_id, current_user)

    try:
        head = s3_client.head_object(Bucket=settings.aws_s3_bucket, Key=key)
        doc.size_bytes = head.get("ContentLength")
    except ClientError as exc:
        if exc.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file not found in storage",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating upload",
        ) from exc

    session.add(doc)
    session.commit()
    session.refresh(doc)

    log_event(
        session=session,
        user_id=current_user.id,
        action="document_upload_completed",
        resource_type="document",
        resource_id=str(doc.id),
        ip_address=request.client.host if request.client else None,
    )

    return {"status": "ok", "document_id": doc.id}
