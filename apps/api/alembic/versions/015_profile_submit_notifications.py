"""Add PROFILE_SUBMITTED notification type and STUDENT_PROFILE entity type.

Revision ID: 015_profile_submit_notifications
Revises: 014_feature_flags
Create Date: 2026-07-11

"""

from collections.abc import Sequence

from alembic import op

revision: str = "015_profile_submit_notifications"
down_revision: str | None = "014_feature_flags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # PostgreSQL requires enum value additions outside a transaction block.
    with op.get_context().autocommit_block():
        op.execute(
            "ALTER TYPE notification_type_enum ADD VALUE IF NOT EXISTS 'PROFILE_SUBMITTED'",
        )
        op.execute(
            "ALTER TYPE notification_entity_type_enum "
            "ADD VALUE IF NOT EXISTS 'STUDENT_PROFILE'",
        )


def downgrade() -> None:
    # Postgres cannot easily remove enum values; leave them in place.
    pass
