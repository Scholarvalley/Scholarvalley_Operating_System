"""ML: consent, recommendation."""
import pytest
from fastapi.testclient import TestClient


def test_ml_consent(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "C", "last_name": "Consent", "latest_education": "BS"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/ml/consent",
        headers=auth_headers,
        json={"applicant_id": aid, "consent_given": True, "version": "v1"},
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_ml_recommendation_no_consent(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "R", "last_name": "Rec", "latest_education": "BA"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/ml/recommendation",
        headers=auth_headers,
        json={"applicant_id": aid, "context": {}},
    )
    assert r.status_code == 200
    data = r.json()
    assert "consent not granted" in data.get("recommendation", "").lower() or "no ml" in data.get("recommendation", "").lower()


def test_ml_recommendation_with_consent(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "R2", "last_name": "Rec2", "latest_education": "BS"},
    )
    aid = cr.json()["applicant_id"]
    client.post(
        "/api/ml/consent",
        headers=auth_headers,
        json={"applicant_id": aid, "consent_given": True, "version": "v1"},
    )
    r = client.post(
        "/api/ml/recommendation",
        headers=auth_headers,
        json={"applicant_id": aid, "context": {}},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["applicant_id"] == aid
    assert "recommendation" in data
