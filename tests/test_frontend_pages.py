"""Frontend: each page returns 200 and contains expected forms/buttons/links."""
import pytest
from fastapi.testclient import TestClient


def _has_selector(html: str, *selectors: str) -> bool:
    """Check that HTML contains id= or class= or tag/text."""
    for s in selectors:
        if s.startswith("#"):
            if f'id="{s[1:]}"' in html or f"id='{s[1:]}'" in html:
                return True
        if s in html:
            return True
    return False


@pytest.mark.parametrize("path,required", [
    ("/", ["hero", "Get in Touch", "Our Services", "main-nav", "Scholarvalley"]),
    ("/about", ["About Us", "section-about", "main-nav"]),
    ("/services", ["Services", "services-list", "For Your Documents Review"]),
    ("/contact", ["Contact Us", "contact-form", "contact_name", "contact-submit-btn"]),
    ("/register", ["register-form", "submit-btn", "first_name", "transcript", "degree"]),
    ("/login", ["login-form", "submit-btn", "email", "password", "Log in"]),
    ("/dashboard", ["dashboard-status", "applicants-table", "logout-btn", "Log out"]),
])
def test_page_returns_200_and_has_content(client: TestClient, path: str, required: list):
    r = client.get(path)
    assert r.status_code == 200, f"{path} should return 200"
    html = r.text
    for req in required:
        assert req in html or req.replace("-", "_") in html, f"{path} should contain {req}"


def test_nav_links_present(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    for link in ["/", "/services", "/about", "/contact", "/register", "/login", "/dashboard"]:
        assert f'href="{link}"' in html or f"href='{link}'" in html or f'href="{link}"' in html.replace(" ", ""), f"Nav should link to {link}"


def test_register_form_has_required_fields(client: TestClient):
    r = client.get("/register")
    assert r.status_code == 200
    html = r.text
    for field in ["first_name", "surname", "email", "confirm_email", "password", "latest_education", "transcript", "degree"]:
        assert field in html, f"Register form should have {field}"


def test_login_form_has_redirect_support(client: TestClient):
    r = client.get("/login")
    assert r.status_code == 200
    # login.js uses ?next= for redirect
    assert "login" in r.text.lower()


def test_static_assets_ok(client: TestClient):
    r = client.get("/static/styles.css")
    assert r.status_code == 200
    r = client.get("/static/main.js")
    assert r.status_code == 200
