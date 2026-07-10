"""Create notifications and notification_preferences tables

Revision ID: 010_notifications
Revises: 009_audit_logs
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_notifications"
down_revision: str | None = "009_audit_logs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

notification_type_enum = postgresql.ENUM(
    "OPPORTUNITY_PUBLISHED",
    "APPLICATION_SUBMITTED",
    "APPLICATION_WITHDRAWN",
    "APPLICATION_STATUS_CHANGED",
    "SHORTLISTED",
    "INTERVIEW_SCHEDULED",
    "OFFER_RELEASED",
    name="notification_type_enum",
    create_type=False,
)

delivery_status_enum = postgresql.ENUM(
    "PENDING",
    "SENT",
    "FAILED",
    "SKIPPED",
    name="notification_delivery_status_enum",
    create_type=False,
)

entity_type_enum = postgresql.ENUM(
    "HIRING_OPPORTUNITY",
    "APPLICATION",
    "SHORTLIST_IMPORT",
    name="notification_entity_type_enum",
    create_type=False,
)


def upgrade() -> None:
    notification_type_enum.create(op.get_bind(), checkfirst=True)
    delivery_status_enum.create(op.get_bind(), checkfirst=True)
    entity_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "recipient_user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("entity_type", entity_type_enum, nullable=True),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "delivery_status",
            delivery_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
    )
    op.create_index(
        "ix_notifications_recipient_user_id",
        "notifications",
        ["recipient_user_id"],
    )
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index(
        "ix_notifications_recipient_unread",
        "notifications",
        ["recipient_user_id", "is_read", "created_at"],
    )

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "email_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "in_app_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_notification_preferences_user_id",
        "notification_preferences",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notification_preferences_user_id",
        table_name="notification_preferences",
    )
    op.drop_table("notification_preferences")
    op.drop_index("ix_notifications_recipient_unread", table_name="notifications")
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_recipient_user_id", table_name="notifications")
    op.drop_table("notifications")
    entity_type_enum.drop(op.get_bind(), checkfirst=True)
    delivery_status_enum.drop(op.get_bind(), checkfirst=True)
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
