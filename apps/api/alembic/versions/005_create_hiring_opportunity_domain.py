"""Create hiring opportunity domain tables

Revision ID: 005_hiring_opportunity_domain
Revises: 004_company_domain
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_hiring_opportunity_domain"
down_revision: str | None = "004_company_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

employment_type_enum = postgresql.ENUM(
    "INTERNSHIP",
    "FULL_TIME",
    "PPO",
    "INTERNSHIP_PPO",
    name="employment_type_enum",
    create_type=False,
)
work_mode_enum = postgresql.ENUM(
    "ONSITE", "HYBRID", "REMOTE", name="work_mode_enum", create_type=False
)
opportunity_status_enum = postgresql.ENUM(
    "DRAFT",
    "PUBLISHED",
    "ARCHIVED",
    name="opportunity_status_enum",
    create_type=False,
)
opportunity_document_type_enum = postgresql.ENUM(
    "JD",
    "ELIGIBILITY",
    "PPT",
    "OTHER",
    name="opportunity_document_type_enum",
    create_type=False,
)
timeline_stage_enum = postgresql.ENUM(
    "DRAFT",
    "PUBLISHED",
    "APPLICATIONS_OPEN",
    "APPLICATIONS_CLOSED",
    "SHORTLIST_RELEASED",
    "ASSESSMENT",
    "INTERVIEW",
    "SELECTED",
    "OFFER_RELEASED",
    "COMPLETED",
    name="timeline_stage_enum",
    create_type=False,
)


def upgrade() -> None:
    employment_type_enum.create(op.get_bind(), checkfirst=True)
    work_mode_enum.create(op.get_bind(), checkfirst=True)
    opportunity_status_enum.create(op.get_bind(), checkfirst=True)
    opportunity_document_type_enum.create(op.get_bind(), checkfirst=True)
    timeline_stage_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "hiring_opportunities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.Column("employment_type", employment_type_enum, nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
        sa.Column("mode", work_mode_enum, nullable=False),
        sa.Column("ctc_min", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("ctc_max", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("bond_details", sa.Text(), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("application_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            opportunity_status_enum,
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hiring_opportunities_company_id", "hiring_opportunities", ["company_id"])
    op.create_index("ix_hiring_opportunities_title", "hiring_opportunities", ["title"])
    op.create_index("ix_hiring_opportunities_status", "hiring_opportunities", ["status"])
    op.create_index("ix_hiring_opportunities_created_by", "hiring_opportunities", ["created_by"])

    op.create_table(
        "eligibility_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hiring_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("minimum_cgpa", sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column("allowed_departments", sa.JSON(), nullable=True),
        sa.Column("allowed_graduation_years", sa.JSON(), nullable=True),
        sa.Column("maximum_active_backlogs", sa.Integer(), nullable=True),
        sa.Column("allow_backlog_history", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("gender_restriction", sa.String(length=20), nullable=True),
        sa.Column("education_requirements", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["hiring_opportunity_id"],
            ["hiring_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hiring_opportunity_id"),
    )
    op.create_index(
        "ix_eligibility_rules_hiring_opportunity_id",
        "eligibility_rules",
        ["hiring_opportunity_id"],
    )

    op.create_table(
        "opportunity_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hiring_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("document_type", opportunity_document_type_enum, nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["hiring_opportunity_id"],
            ["hiring_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunity_documents_hiring_opportunity_id",
        "opportunity_documents",
        ["hiring_opportunity_id"],
    )
    op.create_index(
        "ix_opportunity_documents_uploaded_by",
        "opportunity_documents",
        ["uploaded_by"],
    )

    op.create_table(
        "opportunity_timeline",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hiring_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("stage", timeline_stage_enum, nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["hiring_opportunity_id"],
            ["hiring_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_opportunity_timeline_hiring_opportunity_id",
        "opportunity_timeline",
        ["hiring_opportunity_id"],
    )
    op.create_index(
        "ix_opportunity_timeline_created_by",
        "opportunity_timeline",
        ["created_by"],
    )


def downgrade() -> None:
    op.drop_index("ix_opportunity_timeline_created_by", table_name="opportunity_timeline")
    op.drop_index(
        "ix_opportunity_timeline_hiring_opportunity_id",
        table_name="opportunity_timeline",
    )
    op.drop_table("opportunity_timeline")

    op.drop_index("ix_opportunity_documents_uploaded_by", table_name="opportunity_documents")
    op.drop_index(
        "ix_opportunity_documents_hiring_opportunity_id",
        table_name="opportunity_documents",
    )
    op.drop_table("opportunity_documents")

    op.drop_index("ix_eligibility_rules_hiring_opportunity_id", table_name="eligibility_rules")
    op.drop_table("eligibility_rules")

    op.drop_index("ix_hiring_opportunities_created_by", table_name="hiring_opportunities")
    op.drop_index("ix_hiring_opportunities_status", table_name="hiring_opportunities")
    op.drop_index("ix_hiring_opportunities_title", table_name="hiring_opportunities")
    op.drop_index("ix_hiring_opportunities_company_id", table_name="hiring_opportunities")
    op.drop_table("hiring_opportunities")

    timeline_stage_enum.drop(op.get_bind(), checkfirst=True)
    opportunity_document_type_enum.drop(op.get_bind(), checkfirst=True)
    opportunity_status_enum.drop(op.get_bind(), checkfirst=True)
    work_mode_enum.drop(op.get_bind(), checkfirst=True)
    employment_type_enum.drop(op.get_bind(), checkfirst=True)
