"""Health and static page endpoints."""
import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_frontend_routes_return_html(client: TestClient):
    routes = ["/", "/about", "/services", "/contact", "/register", "/login", "/dashboard"]
    for path in routes:
        r = client.get(path)
        assert r.status_code == 200, f"{path} should return 200"
        assert "text/html" in r.headers.get("content-type", ""), f"{path} should be HTML"
