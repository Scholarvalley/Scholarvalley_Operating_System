"""add applicantreview table

Revision ID: 20260211_review
Revises:
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260211_review"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "applicantreview",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("applicant_id", sa.Integer(), nullable=False),
        sa.Column("reviewer_user_id", sa.Integer(), nullable=False),
        sa.Column("positive", sa.Boolean(), nullable=False),
        sa.Column("feedback", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["applicant_id"], ["applicant.id"]),
        sa.ForeignKeyConstraint(["reviewer_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_applicantreview_applicant_id"), "applicantreview", ["applicant_id"], unique=False)
    op.create_index(op.f("ix_applicantreview_reviewer_user_id"), "applicantreview", ["reviewer_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_applicantreview_reviewer_user_id"), table_name="applicantreview")
    op.drop_index(op.f("ix_applicantreview_applicant_id"), table_name="applicantreview")
    op.drop_table("applicantreview")
