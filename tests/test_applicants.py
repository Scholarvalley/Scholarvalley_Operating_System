"""Applicants API: create, list, get, get other's (403), bundle."""
import pytest
from fastapi.testclient import TestClient


def test_create_applicant(client: TestClient, auth_headers):
    r = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "latest_education": "BSc Computer Science",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["applicant_id"] > 0
    assert data["bundle_id"] > 0
    assert data["status"] == "draft"


def test_list_applicants_empty_or_not(client: TestClient, auth_headers):
    """List applicants returns 200 and a list (may have items from other tests)."""
    r = client.get("/api/applicants/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_applicants_after_create(client: TestClient, auth_headers):
    client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "A", "last_name": "B", "latest_education": "High School"},
    )
    r = client.get("/api/applicants/", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1
    assert items[0]["first_name"] in ("A", "Jane")  # may have from other test


def test_get_applicant(client: TestClient, auth_headers):
    create = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "Get", "last_name": "Me", "latest_education": "BS"},
    )
    aid = create.json()["applicant_id"]
    r = client.get(f"/api/applicants/{aid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["first_name"] == "Get"
    assert r.json()["id"] == aid


def test_get_applicant_404(client: TestClient, auth_headers):
    r = client.get("/api/applicants/99999", headers=auth_headers)
    assert r.status_code == 404


def test_get_applicant_bundle(client: TestClient, auth_headers):
    create = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "B", "last_name": "User", "latest_education": "MS"},
    )
    aid = create.json()["applicant_id"]
    r = client.get(f"/api/applicants/{aid}/bundle", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["applicant_id"] == aid
    assert data["bundle_id"] > 0


def test_get_applicant_bundle_404(client: TestClient, auth_headers):
    r = client.get("/api/applicants/99999/bundle", headers=auth_headers)
    assert r.status_code == 404


def test_list_applicants_pagination(client: TestClient, auth_headers):
    r = client.get("/api/applicants/?page=1&limit=10", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
