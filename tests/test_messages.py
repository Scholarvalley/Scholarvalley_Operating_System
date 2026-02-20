"""Messages: create, list, mark read."""
import pytest
from fastapi.testclient import TestClient


def test_create_message(client: TestClient, auth_headers, manager_headers):
    # Create applicant as client
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "M", "last_name": "Sender", "latest_education": "BS"},
    )
    aid = cr.json()["applicant_id"]
    # Client sends message to manager (we need manager id - use recipient_id from a known user)
    # MessageCreate: applicant_id, recipient_id, body. Sender is current_user.
    r = client.post(
        "/api/messages/",
        headers=auth_headers,
        json={"applicant_id": aid, "recipient_id": None, "body": "Hello, I have a question."},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["body"] == "Hello, I have a question."
    assert data["applicant_id"] == aid
    assert "id" in data


def test_list_messages(client: TestClient, auth_headers):
    r = client.get("/api/messages/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_messages_filter_by_applicant(client: TestClient, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "F", "last_name": "F", "latest_education": "HS"},
    )
    aid = cr.json()["applicant_id"]
    client.post(
        "/api/messages/",
        headers=auth_headers,
        json={"applicant_id": aid, "body": "Test message"},
    )
    r = client.get(f"/api/messages/?applicant_id={aid}", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)


def test_mark_read_404(client: TestClient, auth_headers):
    r = client.post("/api/messages/99999/read", headers=auth_headers)
    assert r.status_code == 404
