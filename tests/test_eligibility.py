"""Eligibility check: success and rule outcomes."""
import pytest
from fastapi.testclient import TestClient


def test_eligibility_eligible_high(client: TestClient, auth_headers):
    # Create applicant first
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "E", "last_name": "High", "latest_education": "BS"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/eligibility/check",
        headers=auth_headers,
        json={"applicant_id": aid, "gpa": 3.8, "toefl": 100},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["is_eligible"] is True
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1


def test_eligibility_eligible_mid(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "M", "last_name": "Mid", "latest_education": "BA"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/eligibility/check",
        headers=auth_headers,
        json={"applicant_id": aid, "gpa": 3.2, "toefl": 85},
    )
    assert r.status_code == 200
    assert r.json()["is_eligible"] is True


def test_eligibility_not_eligible(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "L", "last_name": "Low", "latest_education": "HS"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/eligibility/check",
        headers=auth_headers,
        json={"applicant_id": aid, "gpa": 2.5, "toefl": 70},
    )
    assert r.status_code == 200
    assert r.json()["is_eligible"] is False
    assert "Foundational" in str(r.json().get("recommendations", []))
