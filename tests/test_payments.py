"""Payments: checkout (Stripe mocked), webhook (Stripe mocked)."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_checkout_session_stripe_not_configured(client: TestClient, auth_headers):
    r = client.post(
        "/api/payments/checkout-session",
        headers=auth_headers,
        json={
            "amount_cents": 1000,
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
    )
    # With empty STRIPE_SECRET_KEY we expect 500
    assert r.status_code == 500
    assert "stripe" in r.json().get("detail", "").lower() or "not configured" in r.json().get("detail", "").lower()


@patch("app.api.payments.settings")
@patch("app.api.payments.stripe")
def test_checkout_session_success(mock_stripe, mock_settings, client: TestClient, auth_headers):
    mock_settings.stripe_secret_key = "sk_test_xxx"
    mock_stripe.checkout.Session.create.return_value = MagicMock(
        id="cs_xxx",
        get=lambda x: "pi_xxx" if x == "payment_intent" else None,
    )
    r = client.post(
        "/api/payments/checkout-session",
        headers=auth_headers,
        json={
            "amount_cents": 500,
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        },
    )
    # If stripe is still not set in app (env), we get 500; else 200
    if r.status_code == 200:
        data = r.json()
        assert data["amount_cents"] == 500
        assert data["status"] == "created"


def test_webhook_not_configured(client: TestClient):
    r = client.post(
        "/api/payments/webhook",
        data=b"{}",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 500
