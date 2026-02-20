"""Auth: register, login, validation and error scenarios."""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepass123",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "client"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, session):
    from app.models.user import User
    from app.core.security import hash_password
    u = User(email="dup@example.com", full_name="Dup", hashed_password=hash_password("x"))
    session.add(u)
    session.commit()

    r = client.post(
        "/api/auth/register",
        json={
            "email": "dup@example.com",
            "full_name": "Other",
            "password": "pass123",
        },
    )
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"].lower()


def test_register_invalid_email(client: TestClient):
    r = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "full_name": "X",
            "password": "pass123",
        },
    )
    assert r.status_code == 422


def test_login_success(client: TestClient, auth_headers):
    # auth_headers already created user and logged in; login again
    r = client.post(
        "/api/auth/login",
        data={"username": "authuser@example.com", "password": "pass123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_login_wrong_password(client: TestClient, auth_headers):
    r = client.post(
        "/api/auth/login",
        data={"username": "authuser@example.com", "password": "wrong"},
    )
    assert r.status_code == 400
    assert "incorrect" in r.json()["detail"].lower() or "password" in r.json()["detail"].lower()


def test_login_unknown_user(client: TestClient):
    r = client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "any"},
    )
    assert r.status_code == 400


def test_protected_route_without_token(client: TestClient):
    r = client.get("/api/applicants/")
    assert r.status_code == 401


def test_protected_route_with_token(client: TestClient, auth_headers):
    r = client.get("/api/applicants/", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
