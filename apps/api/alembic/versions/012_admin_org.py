"""Create placement_seasons and enrich departments

Revision ID: 012_admin_org
Revises: 011_admin_users
Create Date: 2026-07-11

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "012_admin_org"
down_revision: str | None = "011_admin_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("departments", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "departments",
        sa.Column(
            "display_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "departments",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "departments",
        sa.Column("logo_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "departments",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.add_column(
        "departments",
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_departments_status", "departments", ["status"])

    op.create_table(
        "placement_seasons",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("academic_batch", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="planning",
        ),
        sa.Column(
            "is_current",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_placement_seasons_name", "placement_seasons", ["name"])
    op.create_index("ix_placement_seasons_status", "placement_seasons", ["status"])
    op.create_index(
        "ix_placement_seasons_is_current",
        "placement_seasons",
        ["is_current"],
    )

    op.add_column(
        "hiring_opportunities",
        sa.Column("season_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_hiring_opportunities_season_id",
        "hiring_opportunities",
        "placement_seasons",
        ["season_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_hiring_opportunities_season_id",
        "hiring_opportunities",
        ["season_id"],
    )

    op.add_column(
        "applications",
        sa.Column("season_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_applications_season_id",
        "applications",
        "placement_seasons",
        ["season_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_applications_season_id", "applications", ["season_id"])

    op.execute("ALTER TYPE audit_entity_type_enum ADD VALUE IF NOT EXISTS 'DEPARTMENT'")
    op.execute(
        "ALTER TYPE audit_entity_type_enum ADD VALUE IF NOT EXISTS 'PLACEMENT_SEASON'",
    )

def downgrade() -> None:
    op.drop_index("ix_applications_season_id", table_name="applications")
    op.drop_constraint("fk_applications_season_id", "applications", type_="foreignkey")
    op.drop_column("applications", "season_id")

    op.drop_index("ix_hiring_opportunities_season_id", table_name="hiring_opportunities")
    op.drop_constraint(
        "fk_hiring_opportunities_season_id",
        "hiring_opportunities",
        type_="foreignkey",
    )
    op.drop_column("hiring_opportunities", "season_id")

    op.drop_index("ix_placement_seasons_is_current", table_name="placement_seasons")
    op.drop_index("ix_placement_seasons_status", table_name="placement_seasons")
    op.drop_index("ix_placement_seasons_name", table_name="placement_seasons")
    op.drop_table("placement_seasons")

    op.drop_index("ix_departments_status", table_name="departments")
    op.drop_column("departments", "archived_at")
    op.drop_column("departments", "updated_at")
    op.drop_column("departments", "logo_url")
    op.drop_column("departments", "status")
    op.drop_column("departments", "display_order")
    op.drop_column("departments", "description")
