"""Admin user management schema updates

Revision ID: 011_admin_users
Revises: 010_notifications
Create Date: 2026-07-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "011_admin_users"
down_revision: str | None = "010_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "user_roles",
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.create_table(
        "user_role_history",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Uuid(),
            sa.ForeignKey("roles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("role_name", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column(
            "performed_by",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_user_role_history_user_id",
        "user_role_history",
        ["user_id"],
    )

    # Extend audit enums (PostgreSQL)
    op.execute("ALTER TYPE audit_entity_type_enum ADD VALUE IF NOT EXISTS 'USER'")
    op.execute("ALTER TYPE audit_action_enum ADD VALUE IF NOT EXISTS 'ROLE_ASSIGNED'")
    op.execute("ALTER TYPE audit_action_enum ADD VALUE IF NOT EXISTS 'ROLE_REMOVED'")


def downgrade() -> None:
    op.drop_index("ix_user_role_history_user_id", table_name="user_role_history")
    op.drop_table("user_role_history")
    op.drop_column("user_roles", "is_primary")
    # Enum values cannot be easily removed on PostgreSQL
