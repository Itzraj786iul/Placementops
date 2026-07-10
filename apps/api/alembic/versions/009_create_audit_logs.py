"""Create audit_logs table

Revision ID: 009_audit_logs
Revises: 008_shortlist_imports
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "009_audit_logs"
down_revision: str | None = "008_shortlist_imports"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

entity_type_enum = postgresql.ENUM(
    "COMPANY",
    "HIRING_OPPORTUNITY",
    "APPLICATION",
    "STUDENT_PROFILE",
    "SHORTLIST_IMPORT",
    "EXPORT",
    name="audit_entity_type_enum",
    create_type=False,
)

action_enum = postgresql.ENUM(
    "CREATE",
    "UPDATE",
    "DELETE",
    "PUBLISH",
    "ARCHIVE",
    "APPLY",
    "WITHDRAW",
    "STATUS_CHANGED",
    "EXPORT_GENERATED",
    "SHORTLIST_IMPORTED",
    "VERIFY",
    name="audit_action_enum",
    create_type=False,
)


def upgrade() -> None:
    entity_type_enum.create(op.get_bind(), checkfirst=True)
    action_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("entity_type", entity_type_enum, nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("action", action_enum, nullable=False),
        sa.Column(
            "performed_by",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "performed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("old_values", sa.JSON(), nullable=True),
        sa.Column("new_values", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
    )
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_performed_at", "audit_logs", ["performed_at"])
    op.create_index("ix_audit_logs_performed_by", "audit_logs", ["performed_by"])
    op.create_index(
        "ix_audit_logs_entity_lookup",
        "audit_logs",
        ["entity_type", "entity_id", "performed_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity_lookup", table_name="audit_logs")
    op.drop_index("ix_audit_logs_performed_by", table_name="audit_logs")
    op.drop_index("ix_audit_logs_performed_at", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity_type", table_name="audit_logs")
    op.drop_table("audit_logs")
    action_enum.drop(op.get_bind(), checkfirst=True)
    entity_type_enum.drop(op.get_bind(), checkfirst=True)
