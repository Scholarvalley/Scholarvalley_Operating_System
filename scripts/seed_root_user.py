#!/usr/bin/env python3
"""
Create the root user so you can log in to the dashboard.

Run from project root:
  python3 scripts/seed_root_user.py

Then log in at http://localhost:8000/login with:
  Email:    root@localhost
  Password: root123
"""

import sys
from pathlib import Path

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.session import engine
from app.models.user import User


EMAIL = "root@localhost"
PASSWORD = "root123"
ROLE = "root"


def main():
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == EMAIL)).first()
        if existing:
            print("Root user already exists. Log in with:")
            print("  Email:   ", EMAIL)
            print("  Password:", PASSWORD)
            return 0

        user = User(
            email=EMAIL,
            full_name="Root",
            hashed_password=hash_password(PASSWORD),
            role=ROLE,
            is_active=True,
        )
        session.add(user)
        session.commit()
        print("Root user created. Log in at http://localhost:8000/login with:")
        print("  Email:   ", EMAIL)
        print("  Password:", PASSWORD)
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
