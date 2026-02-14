from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.api.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_session
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.audit import log_event
from app.services.email import send_email


router = APIRouter()
settings = get_settings()

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


@router.post("/checkout-session", response_model=PaymentRead)
def create_checkout_session(
    payload: PaymentCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe is not configured",
        )

    payment = Payment(
        amount_cents=payload.amount_cents,
        currency=payload.currency,
        applicant_id=payload.applicant_id,
        user_id=current_user.id,
        status="created",
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)

    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency,
                        "unit_amount": payment.amount_cents,
                        "product_data": {
                            "name": "ScholarValley Service",
                        },
                    },
                    "quantity": 1,
                }
            ],
            success_url=payload.success_url,
            cancel_url=payload.cancel_url,
            metadata={
                "payment_id": str(payment.id),
                "user_id": str(current_user.id),
                "applicant_id": str(payload.applicant_id or ""),
            },
        )
    except stripe.error.StripeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error creating Stripe checkout session",
        ) from exc

    payment.stripe_checkout_session_id = checkout_session.id
    payment.stripe_payment_intent_id = checkout_session.get("payment_intent")
    session.add(payment)
    session.commit()
    session.refresh(payment)

    client_ip = request.client.host if request.client else None
    log_event(
        session,
        user_id=current_user.id,
        action="payment_checkout_created",
        resource_type="payment",
        resource_id=str(payment.id),
        metadata={"stripe_checkout_session_id": checkout_session.id},
        ip_address=client_ip,
    )

    return payment


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    session: Session = Depends(get_session),
):
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe webhook is not configured",
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        checkout_session_id = data["id"]

        payment = session.exec(
            select(Payment).where(Payment.stripe_checkout_session_id == checkout_session_id)
        ).first()

        if payment:
            payment.status = "succeeded"
            session.add(payment)
            session.commit()
            session.refresh(payment)

            # Optional: send confirmation email
            if payment.user_id:
                # In a later phase, join User to get email; for now assume lookup
                from app.models.user import User  # local import to avoid cycles

                user = session.get(User, payment.user_id)
                if user and user.email:
                    send_email(
                        [user.email],
                        "Payment received",
                        "<p>Your payment was received successfully.</p>",
                    )

            log_event(
                session,
                user_id=payment.user_id,
                action="payment_succeeded",
                resource_type="payment",
                resource_id=str(payment.id),
                metadata={"stripe_checkout_session_id": checkout_session_id},
                ip_address=request.client.host if request.client else None,
            )

    return {"ok": True}

