"""Add welcome_completed_at for first-login welcome screen.

Revision ID: 016_user_welcome
Revises: 015_profile_submit_notifications
Create Date: 2026-07-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "016_user_welcome"
down_revision: str | None = "015_profile_submit_notifications"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("welcome_completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Existing users should not see the first-login welcome screen.
    op.execute(
        "UPDATE users SET welcome_completed_at = created_at "
        "WHERE welcome_completed_at IS NULL",
    )


def downgrade() -> None:
    op.drop_column("users", "welcome_completed_at")
