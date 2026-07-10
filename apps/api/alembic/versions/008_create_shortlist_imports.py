"""Create shortlist import domain tables

Revision ID: 008_shortlist_imports
Revises: 007_applications_domain
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008_shortlist_imports"
down_revision: str | None = "007_applications_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

match_field_enum = postgresql.ENUM(
    "ROLL_NUMBER",
    "REGISTRATION_NUMBER",
    "EMAIL",
    name="shortlist_match_field_enum",
    create_type=False,
)

import_status_enum = postgresql.ENUM(
    "PREVIEW",
    "CONFIRMED",
    name="shortlist_import_status_enum",
    create_type=False,
)

row_match_status_enum = postgresql.ENUM(
    "MATCHED",
    "UNMATCHED",
    "DUPLICATE",
    "INVALID",
    name="shortlist_row_match_status_enum",
    create_type=False,
)

application_status_enum = postgresql.ENUM(
    "APPLIED",
    "UNDER_REVIEW",
    "SHORTLISTED",
    "ASSESSMENT",
    "INTERVIEW",
    "SELECTED",
    "OFFER_RELEASED",
    "ACCEPTED",
    "REJECTED",
    "WITHDRAWN",
    name="application_status_enum",
    create_type=False,
)


def upgrade() -> None:
    match_field_enum.create(op.get_bind(), checkfirst=True)
    import_status_enum.create(op.get_bind(), checkfirst=True)
    row_match_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "shortlist_imports",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "hiring_opportunity_id",
            sa.Uuid(),
            sa.ForeignKey("hiring_opportunities.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "imported_by",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("match_field", match_field_enum, nullable=False),
        sa.Column("target_status", application_status_enum, nullable=False),
        sa.Column("status", import_status_enum, nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("matched_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unmatched_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_updated", sa.Integer(), nullable=True),
        sa.Column("rows_skipped", sa.Integer(), nullable=True),
        sa.Column(
            "imported_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "shortlist_import_rows",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "import_id",
            sa.Uuid(),
            sa.ForeignKey("shortlist_imports.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("raw_identifier", sa.String(length=255), nullable=False),
        sa.Column("match_status", row_match_status_enum, nullable=False),
        sa.Column(
            "application_id",
            sa.Uuid(),
            sa.ForeignKey("applications.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("student_name", sa.String(length=255), nullable=True),
        sa.Column("current_status", application_status_enum, nullable=True),
        sa.Column("message", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("shortlist_import_rows")
    op.drop_table("shortlist_imports")
    row_match_status_enum.drop(op.get_bind(), checkfirst=True)
    import_status_enum.drop(op.get_bind(), checkfirst=True)
    match_field_enum.drop(op.get_bind(), checkfirst=True)
