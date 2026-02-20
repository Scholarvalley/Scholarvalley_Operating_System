"""Dashboard summary: manager/root only."""
import pytest
from fastapi.testclient import TestClient


def test_dashboard_summary_forbidden_client(client: TestClient, auth_headers):
    r = client.get("/api/dashboard/summary", headers=auth_headers)
    assert r.status_code == 403


def test_dashboard_summary_manager(client: TestClient, manager_headers):
    r = client.get("/api/dashboard/summary", headers=manager_headers)
    assert r.status_code == 200
    data = r.json()
    assert "accepted_clients" in data
    assert "pending_tasks" in data
    assert "total_revenue_cents" in data


def test_dashboard_summary_root(client: TestClient, root_headers):
    r = client.get("/api/dashboard/summary", headers=root_headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["accepted_clients"], int)
    assert isinstance(data["pending_tasks"], int)
    assert isinstance(data["total_revenue_cents"], (int, float))
