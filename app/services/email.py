from __future__ import annotations

from typing import Sequence

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import get_settings


settings = get_settings()

ses_client = boto3.client("ses", region_name=settings.aws_region)


def send_email(
    to_addresses: Sequence[str],
    subject: str,
    html_body: str,
) -> None:
    """
    Send a simple HTML email via AWS SES.

    In production you may want templated emails and richer error handling.
    """
    if not settings.ses_from_email:
        # Misconfigured; in early dev we just no-op.
        return

    try:
        ses_client.send_email(
            Source=settings.ses_from_email,
            Destination={"ToAddresses": list(to_addresses)},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}},
            },
        )
    except (BotoCoreError, ClientError):
        # TODO: add logging/monitoring
        return

