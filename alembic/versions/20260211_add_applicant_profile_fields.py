"""add applicant profile fields

Revision ID: 20260211_profile
Revises: 20260211_review
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260211_profile"
down_revision = "20260211_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("applicant", sa.Column("country_of_residence", sa.String(), nullable=True))
    op.add_column("applicant", sa.Column("study_destination", sa.String(), nullable=True))
    op.add_column("applicant", sa.Column("level_of_study", sa.String(), nullable=True))
    op.add_column("applicant", sa.Column("annual_budget", sa.String(), nullable=True))
    op.add_column("applicant", sa.Column("income_source", sa.String(), nullable=True))
    op.add_column("applicant", sa.Column("service_interest", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("applicant", "service_interest")
    op.drop_column("applicant", "income_source")
    op.drop_column("applicant", "annual_budget")
    op.drop_column("applicant", "level_of_study")
    op.drop_column("applicant", "study_destination")
    op.drop_column("applicant", "country_of_residence")

