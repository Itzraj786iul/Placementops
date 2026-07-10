"""Add optional password_hash for dev login

Revision ID: 006_user_password_hash
Revises: 005_hiring_opportunity_domain
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_user_password_hash"
down_revision: str | None = "005_hiring_opportunity_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
