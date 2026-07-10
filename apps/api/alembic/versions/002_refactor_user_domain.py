"""Refactor users table and add auth_identities

Revision ID: 002_user_domain
Revises: 001_identity
Create Date: 2026-07-09

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_user_domain"
down_revision: str | None = "001_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_user_id", sa.String(length=255), nullable=False),
        sa.Column("provider_email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_user_id", name="uq_auth_provider_identity"),
    )
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])
    op.create_index("ix_auth_identities_provider", "auth_identities", ["provider"])

    op.add_column("users", sa.Column("display_name", sa.String(length=200), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    op.add_column(
        "users",
        sa.Column("status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=True),
    )

    connection = op.get_bind()
    users = connection.execute(
        sa.text(
            "SELECT id, google_id, college_email, first_name, last_name, "
            "profile_picture, is_active FROM users"
        ),
    ).fetchall()

    for row in users:
        display_name = f"{row.first_name} {row.last_name}".strip()
        status = "active" if row.is_active else "inactive"
        connection.execute(
            sa.text(
                "UPDATE users SET display_name = :display_name, avatar_url = :avatar_url, "
                "status = :status, email_verified = :email_verified WHERE id = :id"
            ),
            {
                "display_name": display_name,
                "avatar_url": row.profile_picture,
                "status": status,
                "email_verified": True,
                "id": row.id,
            },
        )
        if row.google_id:
            connection.execute(
                sa.text(
                    "INSERT INTO auth_identities "
                    "(id, user_id, provider, provider_user_id, provider_email, created_at) "
                    "VALUES (:id, :user_id, :provider, :provider_user_id, :provider_email, NOW())"
                ),
                {
                    "id": uuid.uuid4(),
                    "user_id": row.id,
                    "provider": "google",
                    "provider_user_id": row.google_id,
                    "provider_email": row.college_email,
                },
            )

    op.alter_column("users", "display_name", nullable=False)
    op.alter_column("users", "status", nullable=False, server_default="active")
    op.alter_column("users", "email_verified", nullable=False, server_default="false")

    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "google_id")
    op.drop_column("users", "profile_picture")
    op.drop_column("users", "is_active")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column("users", sa.Column("profile_picture", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("google_id", sa.String(length=255), nullable=True))

    connection = op.get_bind()
    users = connection.execute(
        sa.text("SELECT id, avatar_url, status, display_name FROM users"),
    ).fetchall()

    for row in users:
        identity = connection.execute(
            sa.text(
                "SELECT provider_user_id FROM auth_identities "
                "WHERE user_id = :user_id AND provider = 'google' LIMIT 1"
            ),
            {"user_id": row.id},
        ).fetchone()
        connection.execute(
            sa.text(
                "UPDATE users SET profile_picture = :avatar_url, "
                "is_active = :is_active, google_id = :google_id WHERE id = :id"
            ),
            {
                "avatar_url": row.avatar_url,
                "is_active": row.status == "active",
                "google_id": identity.provider_user_id if identity else None,
                "id": row.id,
            },
        )

    op.drop_column("users", "email_verified")
    op.drop_column("users", "status")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")

    op.drop_index("ix_auth_identities_provider", table_name="auth_identities")
    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_table("auth_identities")

    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)
