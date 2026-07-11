"""Create feature_flags and audit entity FEATURE_FLAG

Revision ID: 014_feature_flags
Revises: 013_system_settings
Create Date: 2026-07-11

"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "014_feature_flags"
down_revision: str | None = "013_system_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INITIAL_FLAGS = [
    (
        "student_registration",
        "Student Registration",
        "Allow new student account registration and onboarding.",
    ),
    (
        "student_profile_editing",
        "Student Profile Editing",
        "Allow students to edit their placement profiles.",
    ),
    (
        "student_applications",
        "Student Applications",
        "Allow students to apply to hiring opportunities.",
    ),
    (
        "company_crm",
        "Company CRM",
        "Enable company relationship management for conveners and cell.",
    ),
    (
        "hiring_opportunities",
        "Hiring Opportunities",
        "Enable creation and management of hiring opportunities.",
    ),
    (
        "exports",
        "Exports",
        "Allow generating and downloading placement exports.",
    ),
    (
        "shortlist_import",
        "Shortlist Import",
        "Allow importing shortlists for opportunities.",
    ),
    (
        "notifications",
        "Notifications",
        "Enable in-app notification delivery.",
    ),
    (
        "email_delivery",
        "Email Delivery",
        "Enable outbound email via the configured provider.",
    ),
    (
        "cloud_uploads",
        "Cloud Uploads",
        "Allow file uploads to cloud storage.",
    ),
    (
        "audit_logging",
        "Audit Logging",
        "Record audit events for sensitive actions (critical — cannot disable).",
    ),
    (
        "admin_portal",
        "Admin Portal",
        "Enable Admin Control Center surfaces for operators.",
    ),
    (
        "authentication",
        "Authentication",
        "Core authentication pipeline (critical — cannot disable).",
    ),
]


def upgrade() -> None:
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "scope",
            sa.String(length=30),
            nullable=False,
            server_default="GLOBAL",
        ),
        sa.Column(
            "metadata",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
            name="fk_feature_flags_updated_by",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint("key", name="uq_feature_flags_key"),
    )
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"])
    op.create_index("ix_feature_flags_enabled", "feature_flags", ["enabled"])
    op.create_index("ix_feature_flags_scope", "feature_flags", ["scope"])

    op.execute(
        "ALTER TYPE audit_entity_type_enum ADD VALUE IF NOT EXISTS 'FEATURE_FLAG'",
    )

    flags_table = sa.table(
        "feature_flags",
        sa.column("id", sa.Uuid()),
        sa.column("key", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("enabled", sa.Boolean()),
        sa.column("scope", sa.String()),
        sa.column("metadata", postgresql.JSON()),
    )
    op.bulk_insert(
        flags_table,
        [
            {
                "id": uuid4(),
                "key": key,
                "name": name,
                "description": description,
                "enabled": True,
                "scope": "GLOBAL",
                "metadata": {},
            }
            for key, name, description in INITIAL_FLAGS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_feature_flags_scope", table_name="feature_flags")
    op.drop_index("ix_feature_flags_enabled", table_name="feature_flags")
    op.drop_index("ix_feature_flags_key", table_name="feature_flags")
    op.drop_table("feature_flags")
