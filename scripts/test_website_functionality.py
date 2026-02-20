#!/usr/bin/env python3
"""
End-to-end website functionality test: run against a live server (e.g. after uvicorn).
Checks: every page loads, critical buttons/forms exist, and API flows (health, login) work.

Usage:
  # Start server in another terminal: uvicorn app.main:app --reload
  python scripts/test_website_functionality.py

  # Or with custom base URL:
  BASE_URL=http://localhost:8000 python scripts/test_website_functionality.py
"""
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def get(path: str, **kwargs):
    return requests.get(f"{BASE_URL}{path}", timeout=10, **kwargs)


def post(path: str, **kwargs):
    return requests.post(f"{BASE_URL}{path}", timeout=10, **kwargs)


def main():
    failed = []

    # 1) Health
    try:
        r = get("/health")
        assert r.status_code == 200, r.status_code
        assert r.json().get("status") == "ok"
        print("  OK /health")
    except Exception as e:
        failed.append(f"/health: {e}")
        print(f"  FAIL /health: {e}")
        # If server is down, skip rest
        if "Connection" in str(e) or "refused" in str(e).lower():
            print("\nStart the server first: uvicorn app.main:app --reload")
            sys.exit(1)

    # 2) All static pages return 200 and have key content
    pages = [
        ("/", "Get in Touch", "main-nav"),
        ("/about", "About Us", "section-about"),
        ("/services", "Services", "services-list"),
        ("/contact", "Contact Us", "contact-form"),
        ("/register", "register-form", "transcript"),
        ("/login", "login-form", "Log in"),
        ("/dashboard", "dashboard", "applicants-table"),
    ]
    for path, *must_contain in pages:
        try:
            r = get(path)
            assert r.status_code == 200, f"status {r.status_code}"
            text = r.text
            for s in must_contain:
                assert s in text, f"missing '{s}'"
            print(f"  OK {path}")
        except Exception as e:
            failed.append(f"{path}: {e}")
            print(f"  FAIL {path}: {e}")

    # 3) Login API (wrong credentials) returns 400
    try:
        r = post("/api/auth/login", data={"username": "nonexistent@test.com", "password": "wrong"})
        assert r.status_code == 400
        print("  OK /api/auth/login (wrong creds -> 400)")
    except Exception as e:
        failed.append(f"login API: {e}")
        print(f"  FAIL login API: {e}")

    # 4) Protected route without token returns 401
    try:
        r = get("/api/applicants/")
        assert r.status_code == 401
        print("  OK /api/applicants/ (no token -> 401)")
    except Exception as e:
        failed.append(f"applicants no-auth: {e}")
        print(f"  FAIL applicants no-auth: {e}")

    # 5) Static assets
    for asset in ["/static/styles.css", "/static/main.js"]:
        try:
            r = get(asset)
            assert r.status_code == 200
            print(f"  OK {asset}")
        except Exception as e:
            failed.append(f"{asset}: {e}")
            print(f"  FAIL {asset}: {e}")

    if failed:
        print(f"\n{len(failed)} check(s) failed.")
        sys.exit(1)
    print("\nAll website functionality checks passed.")


if __name__ == "__main__":
    print(f"Testing base URL: {BASE_URL}\n")
    main()
