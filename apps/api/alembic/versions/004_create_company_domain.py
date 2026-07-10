"""Create company CRM domain tables

Revision ID: 004_company_domain
Revises: 003_student_domain
Create Date: 2026-07-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_company_domain"
down_revision: str | None = "003_student_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

company_status_enum = postgresql.ENUM(
    "ACTIVE", "INACTIVE", name="company_status_enum", create_type=False
)
ownership_type_enum = postgresql.ENUM(
    "LEGACY", "NEW", "TRANSFERRED", name="ownership_type_enum", create_type=False
)
pipeline_stage_enum = postgresql.ENUM(
    "NOT_CONTACTED",
    "INVITATION_SENT",
    "FOLLOW_UP_PENDING",
    "HR_REPLIED",
    "MEETING_SCHEDULED",
    "INTERESTED",
    "ON_HOLD",
    "REJECTED",
    "DRIVE_PLANNED",
    name="pipeline_stage_enum",
    create_type=False,
)
communication_type_enum = postgresql.ENUM(
    "EMAIL",
    "CALL",
    "MEETING",
    "WHATSAPP",
    "OTHER",
    name="communication_type_enum",
    create_type=False,
)
company_document_type_enum = postgresql.ENUM(
    "JD",
    "ELIGIBILITY",
    "PPT",
    "OFFER_TEMPLATE",
    "BOND",
    "OTHER",
    name="company_document_type_enum",
    create_type=False,
)


def upgrade() -> None:
    company_status_enum.create(op.get_bind(), checkfirst=True)
    ownership_type_enum.create(op.get_bind(), checkfirst=True)
    pipeline_stage_enum.create(op.get_bind(), checkfirst=True)
    communication_type_enum.create(op.get_bind(), checkfirst=True)
    company_document_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=150), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("linkedin", sa.String(length=500), nullable=True),
        sa.Column("headquarters", sa.String(length=255), nullable=True),
        sa.Column("company_type", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            company_status_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_index("ix_companies_status", "companies", ["status"])
    op.create_index("ix_companies_created_by", "companies", ["created_by"])

    op.create_table(
        "company_contacts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("designation", sa.String(length=150), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("linkedin", sa.String(length=500), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_contacts_company_id", "company_contacts", ["company_id"])

    op.create_table(
        "company_handlers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("handler_user_id", sa.Uuid(), nullable=False),
        sa.Column("branch", sa.String(length=100), nullable=True),
        sa.Column("ownership_type", ownership_type_enum, nullable=False),
        sa.Column("assigned_by", sa.Uuid(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["handler_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_handlers_company_id", "company_handlers", ["company_id"])
    op.create_index(
        "ix_company_handlers_handler_user_id",
        "company_handlers",
        ["handler_user_id"],
    )
    op.create_index("ix_company_handlers_is_active", "company_handlers", ["is_active"])

    op.create_table(
        "company_pipeline",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column(
            "current_stage",
            pipeline_stage_enum,
            nullable=False,
            server_default="NOT_CONTACTED",
        ),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("company_id"),
    )
    op.create_index("ix_company_pipeline_company_id", "company_pipeline", ["company_id"])

    op.create_table(
        "company_communications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("type", communication_type_enum, nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("communication_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_company_communications_company_id",
        "company_communications",
        ["company_id"],
    )
    op.create_index(
        "ix_company_communications_created_by",
        "company_communications",
        ["created_by"],
    )

    op.create_table(
        "company_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("document_type", company_document_type_enum, nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_documents_company_id", "company_documents", ["company_id"])
    op.create_index(
        "ix_company_documents_uploaded_by",
        "company_documents",
        ["uploaded_by"],
    )


def downgrade() -> None:
    op.drop_index("ix_company_documents_uploaded_by", table_name="company_documents")
    op.drop_index("ix_company_documents_company_id", table_name="company_documents")
    op.drop_table("company_documents")

    op.drop_index("ix_company_communications_created_by", table_name="company_communications")
    op.drop_index("ix_company_communications_company_id", table_name="company_communications")
    op.drop_table("company_communications")

    op.drop_index("ix_company_pipeline_company_id", table_name="company_pipeline")
    op.drop_table("company_pipeline")

    op.drop_index("ix_company_handlers_is_active", table_name="company_handlers")
    op.drop_index("ix_company_handlers_handler_user_id", table_name="company_handlers")
    op.drop_index("ix_company_handlers_company_id", table_name="company_handlers")
    op.drop_table("company_handlers")

    op.drop_index("ix_company_contacts_company_id", table_name="company_contacts")
    op.drop_table("company_contacts")

    op.drop_index("ix_companies_created_by", table_name="companies")
    op.drop_index("ix_companies_status", table_name="companies")
    op.drop_index("ix_companies_name", table_name="companies")
    op.drop_table("companies")

    company_document_type_enum.drop(op.get_bind(), checkfirst=True)
    communication_type_enum.drop(op.get_bind(), checkfirst=True)
    pipeline_stage_enum.drop(op.get_bind(), checkfirst=True)
    ownership_type_enum.drop(op.get_bind(), checkfirst=True)
    company_status_enum.drop(op.get_bind(), checkfirst=True)
