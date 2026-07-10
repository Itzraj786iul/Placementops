"""Create applications domain tables

Revision ID: 007_applications_domain
Revises: 006_user_password_hash
Create Date: 2026-07-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007_applications_domain"
down_revision: str | None = "006_user_password_hash"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

application_status_enum = postgresql.ENUM(
    "APPLIED",
    "UNDER_REVIEW",
    "SHORTLISTED",
    "ASSESSMENT",
    "INTERVIEW",
    "SELECTED",
    "OFFER_RELEASED",
    "ACCEPTED",
    "REJECTED",
    "WITHDRAWN",
    name="application_status_enum",
    create_type=False,
)
question_type_enum = postgresql.ENUM(
    "TEXT",
    "BOOLEAN",
    "NUMBER",
    "CHOICE",
    name="question_type_enum",
    create_type=False,
)


def upgrade() -> None:
    application_status_enum.create(op.get_bind(), checkfirst=True)
    question_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "application_questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hiring_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("question_type", question_type_enum, nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("choices", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["hiring_opportunity_id"],
            ["hiring_opportunities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_application_questions_hiring_opportunity_id",
        "application_questions",
        ["hiring_opportunity_id"],
    )

    op.create_table(
        "applications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("hiring_opportunity_id", sa.Uuid(), nullable=False),
        sa.Column("selected_resume_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            application_status_enum,
            nullable=False,
            server_default="APPLIED",
        ),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_by", sa.Uuid(), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hiring_opportunity_id"],
            ["hiring_opportunities.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["selected_resume_id"],
            ["student_resume_library.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_profile_id",
            "hiring_opportunity_id",
            name="uq_applications_student_opportunity",
        ),
    )
    op.create_index(
        "ix_applications_student_profile_id",
        "applications",
        ["student_profile_id"],
    )
    op.create_index(
        "ix_applications_hiring_opportunity_id",
        "applications",
        ["hiring_opportunity_id"],
    )
    op.create_index(
        "ix_applications_selected_resume_id",
        "applications",
        ["selected_resume_id"],
    )
    op.create_index("ix_applications_status", "applications", ["status"])
    op.create_index("ix_applications_submitted_by", "applications", ["submitted_by"])

    op.create_table(
        "application_snapshots",
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_snapshot", sa.JSON(), nullable=False),
        sa.Column("resume_snapshot", sa.JSON(), nullable=False),
        sa.Column("eligibility_snapshot", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("application_id"),
    )

    op.create_table(
        "application_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid(), nullable=False),
        sa.Column("application_question_id", sa.Uuid(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"],
            ["applications.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["application_question_id"],
            ["application_questions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "application_id",
            "application_question_id",
            name="uq_application_answers_application_question",
        ),
    )
    op.create_index(
        "ix_application_answers_application_id",
        "application_answers",
        ["application_id"],
    )
    op.create_index(
        "ix_application_answers_application_question_id",
        "application_answers",
        ["application_question_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_application_answers_application_question_id",
        table_name="application_answers",
    )
    op.drop_index("ix_application_answers_application_id", table_name="application_answers")
    op.drop_table("application_answers")
    op.drop_table("application_snapshots")

    op.drop_index("ix_applications_submitted_by", table_name="applications")
    op.drop_index("ix_applications_status", table_name="applications")
    op.drop_index("ix_applications_selected_resume_id", table_name="applications")
    op.drop_index("ix_applications_hiring_opportunity_id", table_name="applications")
    op.drop_index("ix_applications_student_profile_id", table_name="applications")
    op.drop_table("applications")

    op.drop_index(
        "ix_application_questions_hiring_opportunity_id",
        table_name="application_questions",
    )
    op.drop_table("application_questions")

    question_type_enum.drop(op.get_bind(), checkfirst=True)
    application_status_enum.drop(op.get_bind(), checkfirst=True)
