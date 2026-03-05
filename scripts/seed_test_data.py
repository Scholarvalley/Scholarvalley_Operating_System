#!/usr/bin/env python3
"""
Create root user (if missing) and 2 test applicant profiles with document bundles
so you can log in as admin and see profiles, open them, and review documents.

Run from project root:
  python3 scripts/seed_test_data.py

Then log in at http://localhost:8000/login with:
  Email:    root@localhost
  Password: root123

Go to Dashboard; you will see 2 test applicants. Click an ID to open the profile.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.session import engine
from app.models.applicant import Applicant
from app.models.document import DocumentBundle
from app.models.user import User


ROOT_EMAIL = "root@localhost"
ROOT_PASSWORD = "root123"
ROOT_ROLE = "root"


def main():
    with Session(engine) as session:
        root = session.exec(select(User).where(User.email == ROOT_EMAIL)).first()
        if not root:
            root = User(
                email=ROOT_EMAIL,
                full_name="Root",
                hashed_password=hash_password(ROOT_PASSWORD),
                role=ROOT_ROLE,
                is_active=True,
            )
            session.add(root)
            session.commit()
            session.refresh(root)
            print("Root user created.")
        else:
            print("Root user already exists.")

        existing = session.exec(select(Applicant).where(Applicant.account_user_id == root.id)).all()
        if len(existing) >= 2:
            print("Test applicants already exist ({}). Skipping.".format(len(existing)))
            return 0

        test_profiles = [
            ("Test", "Student One", "High School Diploma, Example High"),
            ("Test", "Student Two", "Bachelor of Arts, Sample University"),
        ]
        for first_name, last_name, latest_education in test_profiles:
            applicant = Applicant(
                account_user_id=root.id,
                first_name=first_name,
                last_name=last_name,
                latest_education=latest_education,
                status="in_review",
            )
            session.add(applicant)
            session.commit()
            session.refresh(applicant)
            bundle = DocumentBundle(
                applicant_id=applicant.id,
                name="Registration documents",
                status="open",
            )
            session.add(bundle)
            session.commit()
            print("Created applicant: {} {} (id={}) with bundle.".format(first_name, last_name, applicant.id))

    print("Done. Log in at http://localhost:8000/login with {} / {}.".format(ROOT_EMAIL, ROOT_PASSWORD))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
