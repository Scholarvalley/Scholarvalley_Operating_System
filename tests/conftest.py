"""
Pytest configuration and fixtures for Scholarvalley API tests.
Use a single SQLite in-memory engine with StaticPool so all connections share the same DB.
"""
import os

# Set test environment before any app import
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-pytest")
os.environ.setdefault("AWS_S3_BUCKET", "test-bucket")
os.environ.setdefault("STRIPE_SECRET_KEY", "")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "")

from app.core.config import get_settings
get_settings.cache_clear()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.db.session import get_session
from app.models.user import User
from app.core.security import hash_password

# One in-memory engine shared by all tests (StaticPool = single connection)
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _get_test_session():
    with Session(_test_engine) as session:
        yield session


@pytest.fixture(scope="session")
def create_tables():
    """Create all tables once. Import models so they register."""
    import app.models.user  # noqa: F401
    import app.models.applicant  # noqa: F401
    import app.models.document  # noqa: F401
    import app.models.payment  # noqa: F401
    import app.models.task  # noqa: F401
    import app.models.message  # noqa: F401
    import app.models.eligibility  # noqa: F401
    import app.models.consent  # noqa: F401
    import app.models.audit  # noqa: F401
    SQLModel.metadata.create_all(bind=_test_engine)
    yield
    _test_engine.dispose()


@pytest.fixture
def client(create_tables):
    """Test client; app uses test DB via override."""
    app.dependency_overrides[get_session] = _get_test_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def session(create_tables):
    """Direct DB session for seeding (same engine as app)."""
    with Session(_test_engine) as s:
        yield s


def _create_user(session, email: str, password: str = "password123", role: str = "client"):
    from sqlmodel import select
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return existing
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=hash_password(password),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, session):
    """Create a user (or use existing), login, return headers with Bearer token."""
    _create_user(session, "authuser@example.com", "pass123")
    session.commit()
    r = client.post(
        "/api/auth/login",
        data={"username": "authuser@example.com", "password": "pass123"},
    )
    assert r.status_code == 200, r.json() if r.status_code != 200 else ""
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_headers(client, session):
    """Create manager user (or use existing), login, return headers."""
    _create_user(session, "manager@example.com", "pass123", role="manager")
    session.commit()
    r = client.post(
        "/api/auth/login",
        data={"username": "manager@example.com", "password": "pass123"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def root_headers(client, session):
    """Create root user (or use existing), login, return headers."""
    _create_user(session, "root@example.com", "pass123", role="root")
    session.commit()
    r = client.post(
        "/api/auth/login",
        data={"username": "root@example.com", "password": "pass123"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
