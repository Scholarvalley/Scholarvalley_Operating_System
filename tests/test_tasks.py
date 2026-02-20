"""Tasks: create (manager), list, patch status."""
import pytest
from fastapi.testclient import TestClient


def test_create_task_forbidden_client(client: TestClient, auth_headers):
    r = client.post(
        "/api/tasks/",
        headers=auth_headers,
        json={"applicant_id": None, "title": "Review", "description": "Review docs"},
    )
    assert r.status_code == 403


def test_create_task_manager(client: TestClient, manager_headers, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "T", "last_name": "Ask", "latest_education": "BS"},
    )
    aid = cr.json()["applicant_id"]
    r = client.post(
        "/api/tasks/",
        headers=manager_headers,
        json={"applicant_id": aid, "title": "Review application", "description": "Check docs"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Review application"
    assert data["status"] == "pending"
    assert data["applicant_id"] == aid


def test_list_tasks(client: TestClient, auth_headers):
    r = client.get("/api/tasks/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_patch_task_status(client: TestClient, manager_headers, auth_headers):
    cr = client.post(
        "/api/applicants/",
        headers=auth_headers,
        json={"first_name": "P", "last_name": "Patch", "latest_education": "MS"},
    )
    aid = cr.json()["applicant_id"]
    tr = client.post(
        "/api/tasks/",
        headers=manager_headers,
        json={"applicant_id": aid, "title": "Task to complete"},
    )
    tid = tr.json()["id"]
    r = client.patch(
        f"/api/tasks/{tid}/status?new_status=completed",
        headers=manager_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_patch_task_404(client: TestClient, auth_headers):
    r = client.patch("/api/tasks/99999/status?new_status=completed", headers=auth_headers)
    assert r.status_code == 404
