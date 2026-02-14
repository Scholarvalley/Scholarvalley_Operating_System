from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.services.audit import log_event
from sqlmodel import Session


router = APIRouter()
settings = get_settings()

s3_client = boto3.client("s3", region_name=settings.aws_region)


@router.post("/initiate")
def initiate_upload(
    content_type: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a presigned URL for client-side S3 upload.

    In a later phase, you will:
    - create a Document DB row
    - associate it with an applicant/bundle
    - enforce virus-scanning workflow
    """
    key = f"uploads/{current_user.id}/{uuid4()}"

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
        action="file_upload_initiated",
        resource_type="s3_object",
        resource_id=key,
        metadata={"content_type": content_type},
        ip_address=request.client.host if request.client else None,
    )

    return {"upload_url": url, "key": key, "content_type": content_type}


@router.post("/complete")
def complete_upload(
    key: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Complete upload callback from client.

    For now this only validates that the object exists. In later phases:
    - validate against expected Document row
    - queue virus scan (S3 event -> Lambda) and mark status in DB
    """
    try:
        s3_client.head_object(Bucket=settings.aws_s3_bucket, Key=key)
    except ClientError as exc:
        if exc.response["ResponseMetadata"]["HTTPStatusCode"] == 404:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded object not found in S3",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating uploaded object",
        ) from exc

    log_event(
        session=session,
        user_id=current_user.id,
        action="file_upload_completed",
        resource_type="s3_object",
        resource_id=key,
        ip_address=request.client.host if request.client else None,
    )

    return {"status": "received", "key": key, "user_id": current_user.id}

